import mvexportutils
import os

def isSupported():
    try:
        mvexportutils.run(['mencoder'])
    except:
        return False
    return True


def encode(kwargs):
    args = []
    args.append('mencoder')

    args.append('mf://' + ','.join(kwargs['imagefiles']))

    # mf_filetype will be either jpg or png
    mf_filetype = (os.path.splitext(kwargs['imagefiles'][0])[1])[1:]

    mf_opts = "w=%d:h=%d:fps=%d:type=%s" % (kwargs['xres'], kwargs['yres'],
					    kwargs['framerate'], mf_filetype)
    args.extend(['-mf', mf_opts])

    audio_preset = {}
    audio_preset['aac'] = ['-oac', 'faac', '-faacopts', 'mpeg=4:raw:br=128']
    audio_preset['mp3'] = ['-oac', 'mp3lame', '-lameopts', 'q=0:aq=2:vbr=2']
    #audio_preset['mp3'] = ['-oac', 'mp3lame', '-lameopts', 'cbr:br=128']

    video_preset = {}
    video_preset['mp4:h264'] = ['-ovc', 'lavc', '-lavcopts',
        'vcodec=libx264:vbitrate=1200:vglobal=1:aglobal=1']
    #    'vcodec=libx264:vbitrate=1200:mbd=2:cmp=2:subcmp=2:trell=yres:v4mv=yes'
    #    ':aic=2:vglobal=1:aglobal=1']
    video_preset['mp4:mpeg4'] = ['-ovc', 'lavc', '-lavcopts',
        'vcodec=mpeg4:vbitrate=5000:mbd=2:cmp=2:subcmp=2:trell=yres:v4mv=yes'
        ':aic=2:vglobal=1:aglobal=1' ":keyint=%g" % kwargs['framerate']]

    video_preset['msmpeg4v2'] = ['-ovc', 'lavc', '-lavcopts',
        'vcodec=msmpeg4v2:vhq:vbitrate=5000' ":keyint=%g" % kwargs['framerate']]	

    format_args = {}
    format_args['mp4'] = ['-of', 'lavf', '-lavfopts',
         'format=mp4']
    #    'format=mp4:i_certify_that_my_video_stream_does_not_use_b_frames']

    # lavc_opts = "vcodec=mpeg4:vbitrate=10000:keyint=%g" % kwargs['framerate']
    # args.extend(['-ovc', 'lavc', '-lavcopts', lavc_opts])
    args.extend(video_preset[kwargs['videopreset']])

    if kwargs.has_key('audiofile') and len(kwargs['audiofile']) > 0:
        args.extend(['-audiofile', kwargs['audiofile']])
        if kwargs.has_key('audiocopy') and kwargs['audiocopy']:
            args.extend(['-oac', 'copy'])
        else:
            args.extend(audio_preset[kwargs['audiopreset']])

    if format_args.has_key(kwargs['outputformat']):
        args.extend(format_args[kwargs['outputformat']])
    
    args.extend(['-o', kwargs['outputfile']])
    #args.extend(['-endpos', "%g" % mvexportutils.videoDuration(kwargs)])
    return mvexportutils.run(args)
