# Seeded with ALDashboard static fixture generator; reviewed against interview YAML.
@e2e
Feature: Complete CLAGuardianship

  Scenario: Prepare a military affidavit using personal knowledge
    Given I start the interview at "military_affidavit_standalone.yml"
    And the maximum seconds for each step is 120
    When I get to "download military_affidavit" with this data:
      | var | value |
      | users[0].name.first | Alex |
      | users[0].name.last | Example |
      | users[0].address.address | 123 Main Street |
      | users[0].address.city | Boston |
      | users[0].address.state | MA |
      | users[0].address.zip | 02108 |
      | user_ask_role | plaintiff |
      | users.there_is_another | False |
      | attorneys.there_are_any | False |
      | other_parties.there_are_any | False |
      | additional_parties.there_are_any | False |
      | users[0].military_status | no |
      | trial_court | all_courts[10] |
      | has_used_scra_site | False |
      | not_used_scra_site_facts | I personally know the party and their military history. |
    Then the question id should be "download military_affidavit"
    And I should see the phrase "All done"
    And I download "military_affidavit.pdf"
