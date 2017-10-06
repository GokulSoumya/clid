#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import os

import npyscreen as npy

from . import base
from . import const
from . import readtag


class SingleEditMetaView(base.ClidEditMetaView):
    """Edit the metadata of a *single* track."""
    def create(self):
        file = self.parentApp.current_files[0]
        meta = readtag.ReadTags(file)
        self.filenamebox = self.add(self._title_textbox, name='Filename',
                                    value=os.path.basename(file).replace('.mp3', ''))
        self.nextrely += 2
        super().create()

        for tbox, field in const.TAG_FIELDS.items():  # show file's tag
            getattr(self, tbox).value = getattr(meta, field)   # str for track_number

    def get_fields_to_save(self):
        return {tag: getattr(self, tbox).value for tbox, tag in const.TAG_FIELDS.items()}

    def do_after_saving_tags(self):
        """Rename the file if necessary."""
        mp3 = self.files[0]
        new_filename = os.path.dirname(mp3) + '/' + self.filenamebox.value + '.mp3'
        if mp3 != new_filename:   # filename was changed
            os.rename(mp3, new_filename)
            main_form = self.parentApp.getForm("MAIN")
            main_form.value.replace_file(old=mp3, new=new_filename)
            main_form.load_files()


class MultiEditMetaView(base.ClidEditMetaView):
    def create(self):
        self.add(npy.Textfield, color='STANDOUT', editable=False,
                 value='Batch tagging {} files'.format(len(self.parentApp.current_files)))
        self.nextrely += 2
        super().create()

    def get_fields_to_save(self):
        # save only those fields which are not empty, to files
        return {tag: getattr(self, tbox).value \
                for tbox, tag in const.TAG_FIELDS.items() \
                if getattr(self, tbox).value}

    def do_after_saving_tags(self):
        pass   # nothing more to do
