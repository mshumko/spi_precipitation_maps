from typing import Iterable
import shutil

def progressbar(iterator: Iterable, iter_length: int=None, text: str=None):
    """
    A terminal progress bar.
    Parameters
    ----------
    iterator: Iterable
        The iterable that will be looped over.
    iter_length: int
        How many items the iterator loop over. If None, will calculate it
        using len(iterator).
    text: str
        Insert an optional text string in the beginning of the progressbar. 
    """
    if text is None:
        text = ''
    else:
        text = text + ':'
    
    if iter_length is None:
        iter_length = len(iterator)

    try:
        for i, item in enumerate(iterator):
            i+=1  # So we end at 100%. Happy users!
            terminal_cols = shutil.get_terminal_size(fallback=(80, 20)).columns
            max_cols = int(terminal_cols-len(text)-10)
            # Prevent a crash if the terminal window is narrower then len(text).
            if max_cols < 0:
                max_cols = 0

            percent = round(100 * i / iter_length)
            bar = "#" * int(max_cols*percent/100)
            print(f'{text} |{bar:<{max_cols}}| {percent}%', end='\r') 
            yield item
    finally:
        print()  # end with a newline. 