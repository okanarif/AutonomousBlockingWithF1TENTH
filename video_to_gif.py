#!/usr/bin/env python3
"""Convert an MP4 video to an animated GIF."""

import cv2
from PIL import Image
from pathlib import Path
import argparse
import sys


def video_to_gif(video_path: str, output_path: str = None, fps: int = 10, scale: float = 1.0):
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    if output_path is None:
        output_path = video_path.with_suffix(".gif")
    else:
        output_path = Path(output_path)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        sys.exit(1)

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / source_fps if source_fps > 0 else 0

    frame_step = max(1, round(source_fps / fps))
    duration_ms = int(1000 / fps)

    print(f"Input  : {video_path}")
    print(f"Output : {output_path}")
    print(f"Source : {source_fps:.1f} fps, {total_frames} frames, {duration_sec:.1f}s")
    print(f"GIF    : {fps} fps, scale={scale}, every {frame_step} frame(s)")

    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_step == 0:
            if scale != 1.0:
                new_w = int(frame.shape[1] * scale)
                new_h = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb))

        frame_idx += 1

    cap.release()

    if not frames:
        print("Error: No frames extracted.")
        sys.exit(1)

    print(f"Saving {len(frames)} frames → {output_path} ...")
    frames[0].save(
        str(output_path),
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration_ms,
        optimize=False,
    )
    print(f"Done! GIF saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert MP4 video to animated GIF")
    parser.add_argument("video", nargs="?",
                        default="/home/okanarif/Downloads/Project_Video.mp4",
                        help="Path to input MP4 file")
    parser.add_argument("-o", "--output", default=None,
                        help="Output GIF path (default: same location as input)")
    parser.add_argument("--fps", type=int, default=10,
                        help="GIF frame rate (default: 10)")
    parser.add_argument("--scale", type=float, default=0.5,
                        help="Resize scale factor, e.g. 0.5 = half size (default: 0.5)")
    args = parser.parse_args()

    video_to_gif(args.video, args.output, args.fps, args.scale)


if __name__ == "__main__":
    main()
