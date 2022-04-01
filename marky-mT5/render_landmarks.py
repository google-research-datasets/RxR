"""Basic script for rendering RxR silver landmarks."""

import collections
import gzip
import json
import math
import pathlib
import time

import MatterSim
import numpy as np
from PIL import Image

SILVER_LANDMARK_PATHS = [
    'rxr_landmarks_train_guide.jsonl.gz',
    'rxr_landmarks_val_seen_guide.jsonl.gz',
    'rxr_landmarks_val_unseen_guide.jsonl.gz'
]

OUTDIR = 'landmarks'
IMG_SIZE = 300  # Set the maximum dimension.


def read_jsonlines(paths):
  for path in paths:
    with gzip.open(path, 'r') as f:
      for line in f:
        yield json.loads(line)


def init_sim(h_fov, v_fov):
  """Initialize the Matterport3D Simulator for a given field-of-view."""
  simulator = MatterSim.Simulator()
  simulator.setCameraVFOV(v_fov)
  # Calculate the appropriate image height and width for the field-of-view.
  # The provided IMG_SIZE will be the larger image dimension.
  if h_fov > v_fov:
    width = IMG_SIZE
    height = int(math.tan(v_fov / 2.0) * width / math.tan(h_fov / 2.0))
  else:
    height = IMG_SIZE
    width = int(math.tan(h_fov / 2.0) * height / math.tan(v_fov / 2.0))
  simulator.setCameraResolution(width, height)
  simulator.setDepthEnabled(False)
  simulator.initialize()
  return simulator


if __name__ == '__main__':

  # Cluster landmarks with the same fov for faster rendering.
  landmarks = collections.defaultdict(list)
  total = 0
  for item in read_jsonlines(SILVER_LANDMARK_PATHS):
    for i, (heading, pitch, hfov,
            vfov) in enumerate(item['landmark_angle_coords']):
      total += 1
      landmarks[(hfov, vfov)].append(
          ((item['scan'], item['landmark_source_panos'][i], heading,
            pitch), item['split'], item['language'], item['instruction_id'], i,
           item['text_spans'][i]))

  # Start rendering using the Matterport3D simulator.
  start = time.time()
  count = 0
  for key in landmarks:
    hfov, vfov = key
    sim = init_sim(hfov, vfov)
    for (scan, pano, heading,
         pitch), split, lang, instr_id, ix, landmark_phrase in landmarks[key]:
      sim.newEpisode([scan], [pano], [heading], [pitch])
      state = sim.getState()[0]
      im = Image.fromarray(np.array(state.rgb, copy=False)[:, :, ::-1])
      out_path = '%s/%s/%s/%d' % (OUTDIR, split, lang, instr_id)
      pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
      im.save('%s/%d-%s.png' %
              (out_path, ix, landmark_phrase.replace('/', '-')))
      count += 1

      if count % 1000 == 0:
        mins = (time.time() - start)/60.
        total_mins = total / count * mins
        print('%d complete in %.f minutes, projected %.f minutes total' %
              (count, mins, total_mins))


