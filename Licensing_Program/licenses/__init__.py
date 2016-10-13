"""Submodule for getting license information and text.
Current assumption about licenses is that they all have the word 'Copyright'
in the first line of their file header.
"""

import licenses.gpl_2
import licenses.gpl_3
import licenses.mit


license_dict = {
    "gpl-2" : licenses.gpl_2,
    "gpl-3" : licenses.gpl_3,
    "mit" : licenses.mit,
}
