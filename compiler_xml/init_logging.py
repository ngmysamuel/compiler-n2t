import logging

logger = logging.getLogger(__name__)

def set_level(level):
  match level:
    case "d":
      logging.basicConfig(filename='mylog.log', filemode='w', format='%(message)s', level=logging.DEBUG)
    case "i":
      logging.basicConfig(filename='mylog.log', filemode='w', format='%(message)s', level=logging.INFO)
    case "w":
      logging.basicConfig(filename='mylog.log', filemode='w', format='%(message)s', level=logging.WARNING)