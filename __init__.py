# from typing import overload
import cv2
import numpy as np

Cv2Image = FrameType = np.ndarray

class VideoHandler(object):
  def __init__(self, video:str|cv2.VideoCapture|'VideoHandler') -> None:
    '''
    Pass a VideoHandler instance will share de VideoCapture object, 
    not create a new cv2.VideoCapture instance.
    '''
    if isinstance(video, str):
      video = cv2.VideoCapture(video)
    elif isinstance(video, VideoHandler):
      video = video.video
    self.video = video

  @property
  def cur_frame(self, /):
    """
    Return current frame number. Same as #get_frame_number
    """
    return int(self.video.get(cv2.CAP_PROP_POS_FRAMES))

  @staticmethod
  def open(path:str):
    """
    Returns a VideoHandler object with a opened cv2 video capture. 
    It's the same to VideoHandler(path) or 
    VideoHandler(cv2.VideoCapture(path))
    """
    return VideoHandler(path)

  # cv2.VideoCapture methods
  def grab(self, /) -> bool:
    '''The same as the VideoCapture method'''
    return self.video.grab()

  def retrieve(self, /) -> tuple[bool,Cv2Image]:
    '''The same as the VideoCapture method'''
    return self.video.retrieve()
  # @overload
  # def retrieve(self, image:Cv2Image, /) -> tuple[bool,Cv2Image]: ...
  # @overload
  # def retrieve(self, frame_index:int, /) -> tuple[bool,Cv2Image]: ...
  # @overload
  # def retrieve(self, image:Cv2Image, frame_index:int, /) -> tuple[bool,Cv2Image]: ...
  # @overload
  # def retrieve(self, flag, /) -> tuple[bool,Cv2Image]: ...
  # @overload
  # def retrieve(self, image:Cv2Image, flag, /) -> tuple[bool,Cv2Image]: ...
  # @overload
  # def retrieve(self, /) -> tuple[bool,Cv2Image]:
  #   '''The same as the VideoCapture method'''
  #   ...
  # def retrieve(self, *args) -> tuple[bool,Cv2Image]:
  #   if args:
  #     return self.video.retrieve(*args)
  #   return self.video.retrieve()
  def retrieve(self) -> tuple[bool,Cv2Image]:
    '''The same as the VideoCapture method (without params)'''
    return self.video.retrieve()

  def read(self, /) -> tuple[bool,Cv2Image]:
    '''The same as the VideoCapture method'''
    return self.video.read()

  def release(self, /):
    '''The same as the VideoCapture method'''
    return self.video.release()

  def isOpened(self, /) -> bool:
    '''The as VideoCapture method'''
    return self.video.isOpened()

  def get_prop(self, prop_id:int, /):
    """Alias to cv2 method video.get(prop_id)"""
    return self.video.get(prop_id)

  def set_prop(self, prop_id:int, value, /):
    """Alias to cv2 method video.set(prop_id, value)"""
    return self.video.set(prop_id, value)

  # Simplification methods
  def skip(self, amount=1, /):
    """
    Discart frames without decode by calling #grab
    multiple times. Stop if grab call return False
    :amount: The number of frames that will be grabbed
    returns remaining of passed amount (0 on complete skip)
    """
    while amount > 0:
      amount -= 1
      if not self.grab():
        break
    return amount

  def next(self, /):
    """
    Grab, decode and return the next frame using #read method. 
    Returns None if can't.
    """
    success, frame = self.read()
    return frame if success else None

  # def retrieve_next(self, /):
  #   """
  #   Grab, decode and return the next frame using #retrieve method. 
  #   Returns None if can't.
  #   """
  #   success, frame = self.retrieve()
  #   if success: return frame
  #   return None

  def close(self, /):
    """Close video calling #release"""
    self.release()

  def to_frame(self, frame_number:int, /):
    '''Set current frame position to passed frame number'''
    # self.to_frame_index(frame_number-1)
    self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)

  def to_frame_index(self, frame_index:int, /):
    '''
    Set current frame position to passed frame index (starting
    by zero)
    '''
    self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

  def to_secs(self, secs:float, /):
    '''
    Goes to passed video seconds by setting opencv CAP_PROP_POS_MSEC. 
    Not perfect.
    '''
    return self.video.set(cv2.CAP_PROP_POS_MSEC, secs*1000)

  def to_secs2(self, secs:float, /):
    """
    Goes to passed video secondss. Uses floor frame number 
    calculated by using fps. Not perfect.
    """
    frame_number = self.get_fps()*secs
    return self.to_frame(int(frame_number))

  def to_ms(self, ms:float, /):
    '''
    Goes to passed video milliseconds by setting opencv
    CAP_PROP_POS_MSEC. Not perfect.
    '''
    return self.video.set(cv2.CAP_PROP_POS_MSEC, ms)

  def to_ms2(self, ms:float, /):
    """
    Set video to passed milli seconds. Not perfect. 
    Uses floor frame number calculated by using fps.
    """
    frame_number = self.get_fps()*ms/1000
    return self.to_frame(int(frame_number))

  def to_ratio(self, ratio:float, /):
    return self.video.set(cv2.CAP_PROP_POS_AVI_RATIO, ratio)

  def to_ratio2(self, ratio:float, /):
    '''Set current position based on values between 0-1'''
    frame = int(ratio * self.get_total_frames())
    return self.to_frame(frame)

  def get_secs(self, /):
    """
    Returns current seconds based on current frame number and 
    video fps. Not perfect.
    """
    return self.frame2secs(self.get_cur_frame())

  def get_ms(self, /):
    """ Returns current milliseconds. """
    return self.video.get(cv2.CAP_PROP_POS_MSEC)

  def get_ms2(self, /):
    """
    Returns current milliseconds based on current frame number 
    and video fps. Not perfect.
    """
    return self.frame2ms(self.get_cur_frame())

  def get_ratio(self, /) -> float:
    """
    Returns current position in a range of 0-1.
    """
    return self.video.get(cv2.CAP_PROP_POS_AVI_RATIO)

  def get_ratio2(self, /):
    """
    Returns current position in a range of 0-1 based on 
    frame number.
    """
    return self.cur_frame/self.get_total_frames()

  # Utils
  def frame2secs(self, frame_number:int):
    """
    Return the seconds relative to frame_number using video fps. Not perfect;
    Works like #get_secs but independs from current position.
    :frame_number: frame position to convert to seconds
    """
    return frame_number/self.get_fps()

  def frame2ms(self, frame_number:int):
    """
    Return the milliseconds relative to frame_number using 
    video fps. Not perfect. Works like #get_ms but independs
    from current position.
    :frame_number: frame number to convert to seconds
    """
    return frame_number/(self.get_fps()*1000)

  def secs2frame(self, secs:float):
    """
    Return the rounded frame number relative to passed seconds 
    using video fps. Not perfect.
    """
    return round(secs * self.get_fps())

  def ms2frame(self, ms:float):
    """
    Return the rounded frame number relative to passed milli 
    seconds using video fps. Not perfect.
    """
    return round(self.get_fps() * ms/1000)

  # Video info getters
  def get_frame_dimensions(self, /):
    """Return frame dimensions (width, height)"""
    return (self.get_frame_width(), self.get_frame_height())

  def get_frame_height(self, /):
    """Return frame height"""
    r = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return int(r)

  def get_frame_width(self, /):
    """Return frame width"""
    r = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
    return int(r)

  def get_fps(self, /) -> float:
    """Return video frames per second (FPS)"""
    return self.video.get(cv2.CAP_PROP_FPS)

  def get_total_frames(self, /):
    """Return current total frame amount."""
    total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
    return int(total_frames)

  def get_frame_number(self, /):
    """Return current frame number."""
    frame_number = self.video.get(cv2.CAP_PROP_POS_FRAMES)
    return int(frame_number)

  def get_info(self, /):
    return VideoInfo(self)

  def __iter__(self, /):
    """
    Retuns a generetor that iterates through video calling next 
    until it returns None
    """
    while not (frame := self.next()) is None:
      yield frame

class VideoInfo(object):
  def __init__(self, video:'VideoHandler|cv2.VideoCapture') -> None:
    if not isinstance(video, VideoHandler):
      video = VideoHandler(video)
    self.frame_size = video.get_frame_size()
    self.total_frames = video.get_total_frames()
    self.fps = video.get_fps()

  @property
  def frame_width(self): return self.frame_size[0]

  @property
  def frame_height(self): return self.frame_size[1]

# class VideoIterator(object):
#   def __init__(
#       self, video:VideoHandler, 
#       count_lim:'int|None'=None
#   ) -> None:
#     if not count_lim is None:
#       count_lim = video.get_total_frames()
#     self.count_lim = count_lim
#     self.video = video

#   def __iter__(self, /):
#     for _ in range(0, self.count_lim):
#       frame = self.video.next()
#       if frame is None:
#         break
#       yield frame

class VideoIterator(object):
  def __init__(
      self, video:VideoHandler, 
      count_lim:'int|None'=None
  ) -> None:
    '''
    Creates a iterator that iterates through the :video: using
    video.next() calls. Stops after reach :count_lim: or when
    video.next returns None.
    Note the :count_lim: is used with internal count, and 
    not with video frame position, so external changes on 
    video position not is noticied by iterator. 

    Eg. passing 10 as count_lim with a video at frame 
    index at 0, if you skip a total of 5 frames, the iterator
    will stops at frame 15 (or less if can't).
    '''
    self.count_lim = count_lim
    self.video = video

  def __iter__(self, /):
    if self.count_lim is None:
      while (frame:=self.video.next()) is not None:
        yield frame
    else:
      for _ in range(0, self.count_lim):
        frame = self.video.next()
        if frame is None:
          break
        yield frame

class Scene(VideoHandler):
  def __init__(
      self, video:'VideoHandler|cv2.VideoCapture',
      start=0, end_exclusive:'int|None'=None
    ):
    """
    Is a VideoHandler subtype to simplify iterations through 
    a range of frames.
    Note that will use the passed video handler to iterate, 
    so its will change the frame position of video
    :video: video to use interval of
    :start: frame index to start of
    :end_exclusive: frame index to stop iteration (exclusive)
    """
    super().__init__(video)
    self.start = start
    self.end = end_exclusive or self.get_total_frames()

  def reset(self, /):
    self.to_frame(self.start)

  def __iter__(self, /):
    """
    Retuns a generetor that iterates through video calling next in 
    the range(video current_frame, self.end) or until it returns None
    """
    for _ in range(self.get_cur_frame(), self.end):
      frame = self.next()
      if frame is None:
        break
      yield frame
