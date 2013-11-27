# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


import re
from wtforms.validators import ValidationError, StopValidation, Regexp
from invenio.usercollection_model import UserCollection

class RequiredIf(object):
    """
    """
    def __init__(self, other_field_name, values, message=None):
        self.other_field_name = other_field_name
        self.values = values
        self.message = message

    def __call__(self, form, field):
        try:
            other_field = getattr(form, self.other_field_name)
            other_val = other_field.data
            if other_val in self.values:
                if not field.data or isinstance(field.data, basestring) and not field.data.strip():
                    if self.message is None:
                        self.message = 'This field is required.'
                    field.errors[:] = []
                    raise StopValidation(self.message % {'other_field': other_field.label.text, 'value': other_val})
        except AttributeError:
            pass


doi_validator = Regexp("(^$|(doi:)?10\.\d+(.\d+)*/.*)", flags=re.I, message="The provided DOI is invalid - it should look similar to '10.1234/foo.bar'.")

def doi_prefix_validator(form, field):
    from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME
    field_doi = field.data
    pub = getattr(form, '_pub', None)

    if pub:
        reserved_doi = pub._metadata.get("__doi__", None)
        if reserved_doi and reserved_doi != field_doi and field_doi.startswith("%s/" % CFG_DATACITE_DOI_PREFIX):
            raise ValidationError('You are not allowed to edit a pre-reserved DOI. Click the Pre-reserve DOI button to resolve the problem.')

    elif field_doi.startswith("%s/" % CFG_DATACITE_DOI_PREFIX):
        raise ValidationError('The prefix %s is administered automatically by %s. Please leave the field empty or click the "Pre-reserve DOI"-button and we will assign you a DOI.' % (CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME))

    if CFG_DATACITE_DOI_PREFIX != "10.5072" and field_doi.startswith("10.5072/"):
        raise ValidationError('The prefix 10.5072 is invalid. The prefix is only used for testing purposes, and no DOIs with this prefix are attached to any meaningful content.')


def community_validator(form, field):
    if field.data:
        ids = map(lambda x: x.get('identifier'), field.data)
        query = UserCollection.query.filter(UserCollection.id.in_(ids)).all()
        if not ids or len(query) == len(ids):
            return True

        found = map(lambda x: x.id, query)
        for i in ids:
            if i not in found:
                raise ValidationError("Invalid community identifier: %s" % i)