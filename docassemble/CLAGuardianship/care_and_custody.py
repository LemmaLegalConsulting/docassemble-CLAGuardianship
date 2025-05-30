from typing import Optional
from docassemble.base.util import (
    DAObject,
    DAList,
    comma_and_list,
    validation_error,
    word,
)
from docassemble.AssemblyLine.al_general import *
import re

__all__ = [
    "OtherProceeding",
    "OtherProceedingList",
    "GAL",
    "GALList",
    "number_to_letter",
    "filter_letters",
    "include_a_year",
]


class OtherProceeding(DAObject):
    """Currently used to represents a care and custody proceeding."""

    def init(self, *pargs, **kwargs):
        super(OtherProceeding, self).init(*pargs, **kwargs)
        if not hasattr(self, "children"):
            self.initializeAttribute("children", ALPeopleList)
        if not hasattr(self, "attorneys"):
            self.initializeAttribute("attorneys", ALPeopleList)
        if not hasattr(self, "attorneys_for_children"):
            self.initializeAttribute("attorneys_for_children", ALPeopleList)
        if not hasattr(self, "other_parties"):
            self.initializeAttribute("other_parties", ALPeopleList)
        if not hasattr(self, "gals"):
            self.initializeAttribute("gals", GALList.using(ask_number=True))

    # We use a property decorator because Docassemble expects this to be an attribute, not a method
    @property
    def complete_proceeding(self):
        """Tells docassemble the list item has been gathered when the variables named below are defined."""
        # self.user_role # Not asked for adoption cases
        self.case_status
        self.children.gathered
        self.other_parties.gather()
        # if self.is_open:
        #   self.atty_for_user
        #   if self.atty_for_children:
        #     if len(self.children) > 1:
        #       self.attorneys_for_children.gather()
        #   if self.has_gal:
        #     self.gals.gather()
        #   else:
        #     self.gals.auto_gather=True
        #     self.gals.gathered=True
        return True
        # We're going to gather this per-attorney instead of
        # per-case now
        # if self.case_status == 'pending':
        #  self.attorneys.gather()

    def child_letters(self):
        """Return ABC if children lettered A,B,C are part of this case"""
        return "".join([child.letter for child in self.children if child.letter])

    def status(self):
        """Should return the status of the case, suitable to fit on Section 7 of the affidavit disclosing care or custody"""
        if not self.is_open:
            return "Closed"
        else:
            return "Open"

    def role(self):
        """Return the letter representing user's role in the case. If it's an adoption case, don't return a role."""
        if self.case_status == "adoption":
            return ""
        return self.user_role

    def case_description(self):
        """Returns a short description of the other case or proceeding meant to display to identify it
        during list gathering in the course of the interview"""
        description = ""
        description += self.case_status.title() + " case in "
        description += self.court_name
        if hasattr(self, "docket_number") and len(self.docket_number.strip()):
            description += ", case number: " + self.docket_number
        description += " (" + str(self.children) + ")"
        return description

    def __str__(self):
        return self.case_description()


class OtherProceedingList(DAList):
    """Represents a list of care and custody proceedings"""

    def init(self, *pargs, **kwargs):
        super(OtherProceedingList, self).init(*pargs, **kwargs)
        self.object_type = OtherProceeding
        self.complete_attribute = "complete_proceeding"  # triggers the complete_proceeding method of an OtherProceeding

    def includes_adoption(self):
        """Returns true if any of the listed proceedings was an adoption proceeding."""
        for case in self.elements:
            if case.case_status == "adoption":
                return True


class GAL(ALIndividual):
    """This object has a helper for printing itself in PDF, as well as a way to merge attributes for duplicates"""

    def status(self):
        return str(self) + " (" + comma_and_list(self.represented_children) + ")"

    def is_match(self, new_gal):
        return str(self) == str(new_gal)

    def merge(self, new_gal):
        self.represented_children = PeopleList(
            elements=self.represented_children.union(new_gal.represented_children)
        )


class GALList(ALPeopleList):
    """For storing a list of Guardians ad Litem in Affidavit of Care and Custody"""

    def init(self, *pargs, **kwargs):
        super(GALList, self).init(*pargs, **kwargs)
        self.object_type = GAL

    def append(self, new_item, set_instance_name=False):
        """Only append if this GAL has a unique name"""
        match = False
        for item in self:
            if item.is_match(new_item):
                match = True
                # Merge list of children represented if same name
                item.merge(new_item)
        if not match:
            return super().append(new_item, set_instance_name=set_instance_name)
        return None


def number_to_letter(n):
    """Returns a capital letter representing ordinal position. E.g., 1=A, 2=B, etc. Appends letters
    once you reach 26 in a way compatible with Excel/Google Sheets column naming conventions. 27=AA, 28=AB...
    """
    string = ""
    if n is None:
        n = 0
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def filter_letters(letter_strings):
    """Used to take a list of letters like ["A","ABC","AB"] and filter out any duplicate letters."""
    # There is probably a cute one liner, but this is easy to follow and
    # probably same speed
    unique_letters = set()
    if isinstance(letter_strings, str):
        letter_strings = [letter_strings]
    for string in letter_strings:
        if string:  # Catch possible None values
            for letter in string:
                unique_letters.add(letter)
    try:
        retval = "".join(sorted(unique_letters))
    except:
        retval = ""
    return retval


def include_a_year(text: str, field: Optional[str] = None) -> bool:
    """
    Validates whether the input text contains at least one 4-digit sequence
    that occurs within a range of ~ 200 years, indicating a valid "year"
    for an event that should be reported on most court forms, like a birthdate
    or a moving date.

    Returns True if found, otherwise raises a DAValidationError.
    """
    # Match a 4-digit sequence
    if re.search(r"\b(18|19|20|21)\d{2}\b", text):
        return True
    else:
        validation_error(word("Include a year, like: Fall of 2023"), field=field)

    return False
