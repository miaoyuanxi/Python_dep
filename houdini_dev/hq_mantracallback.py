import math
import os
import sys
import mantra, hqlib, cloud, hutil.json

# Note that this file is run after each tile renders, and that the variables
# are preserved from run to run.

num_completed_tiles = mantra.property("tile:ncomplete")[0]
num_tiles = mantra.property("tile:ntiles")[0]

if "updateProgress" not in locals():
    # This is the first tile in the current image, so this is where we define
    # functions and set up global variables.
    def outputImageFileName():
        """Return the name of the current file being generated."""
        file_name = mantra.property("image:filename")[0]
        if file_name == "null:":
            # The file name is "null:" when generating shadow map files.
            # Look for the filename value in the deepresolver property.
            resolver_properties = mantra.property("image:deepresolver")
            if "filename" in resolver_properties:
                file_name = resolver_properties[
                    resolver_properties.index("filename") + 1]
        return file_name

    def updateProgress(num_completed_tiles):
        """If the completion percentage has changed, print out a message that
        HQueue will parse.
        """
        global _expected_image_path
        global _prev_frame_progress
        global _prev_total_progress

        # Check if the current file being written from this ifd is the desired
        # one (since ifd's can generate multiple files such as shadow maps).
        # If it is not, then we do not output progress messages or else
        # the progress percentage will appear to reset after it completes
        # one image and moves on to the next.
        _is_final_image = False
        if _expected_image_path is not None:
            _is_final_image = (outputImageFileName() == _expected_image_path)
        else:
            # We have no idea what the expected image path is suppose to be
            # so we make an educated guess.
            file_name = mantra.property("image:filename")[0]
            if file_name != "null:":
                _is_final_image = True

        if not _is_final_image:
            return

        # Calculate the frame's completion percentage.  Truncate to 2 decimal
        # places.  We do not round or else we might accidentally round up to
        # 100% for renders that are *almost* finished.
        frame_progress = num_completed_tiles / float(num_tiles)
        frame_progress = math.floor(frame_progress * 100) / 100

        # Notify the render tracker of our render progress.
        if _render_tracker_rpc is not None \
            and frame_progress != _prev_frame_progress:
            _render_tracker_rpc.setFrameRenderFraction(
                _project_name, _frame, frame_progress)

        total_progress = "%.02f/%i" % (
            _frame_index + frame_progress, _num_frames)

        # Output the total job progress.
        if total_progress != _prev_total_progress:
            print "PROGRESS:", total_progress
            sys.stdout.flush()
       
        # Keep track of our progress.
        _prev_frame_progress = frame_progress
        _prev_total_progress = total_progress


    # Cache the arguments passed to the script.
    _frame_index = int(sys.argv[1])
    _frame = int(sys.argv[2])
    _num_frames = int(sys.argv[3])
    _project_name = sys.argv[4]
    _contact_render_tracker = int(sys.argv[5])

    _prev_frame_progress = None
    _prev_total_progress = None

    if _contact_render_tracker:
        _render_tracker_rpc = hqlib.getRenderTrackerRPC()
    else:
        _render_tracker_rpc = None

    # Get the expected image path.
    # This is needed to determine if the image currently being rendered
    # is the final output image.
    _expected_image_path = None
    if _render_tracker_rpc is not None:
        _expected_image_path = _render_tracker_rpc.getImagePath(
            _project_name, _frame)

if num_completed_tiles > 0 and "updateProgress" in locals():
    try:
        updateProgress(num_completed_tiles)
    except:
        pass
