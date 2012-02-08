import sys
frame = sys._getframe()
backframe = str(frame.f_back.f_code)
if 'nose' not in backframe and 'unittest' not in backframe:
    # dont raise here just because nose or unittest tried to import us
    import doesnt.exist
