import logging
import pandas as pd
from typing import Dict, List, Tuple
from data_models.processed_git_data import ProcessedGitData, RawStatsType
from utils.email_matcher import EmailMatcher


logger = logging.getLogger(__name__)

PredictionsType = Dict[str, List[str]]

SMALL_SKILLS = [
    "Ant Build System",
    "ApacheConf",
    "AutoHotkey",
    "Awk",
    "Batchfile",
    "CMake",
    "Dockerfile",
    "Git Attributes",
    "Git Config",
    "Makefile",
    "Maven POM",
    "Nginx",
    "Shell"
]


class SkillsPredictor:
    """
    Handles doing predictions from a raw set of stats that are
    processed from the commit logs of a git repository.
    """

    def __init__(self):
        self.email_matcher = EmailMatcher()

    def predict(self, raw_stats: List[RawStatsType], existing_emails: List[str] = []) -> PredictionsType:
        """
        Perform the skills predictions against a set of raw stats from a git repo.

        @param raw_stats: A map of raw stat data from the Scraper service that looks like the following:

        {
            "author": [],
            "oldestCommitDate": [],
            "latestCommitDate": [],
            "changeCount": [],
            "commit": [],
            "file": [],
            "skill": [],
            "repo": []
        }

        @return: A dictionary containing the predictions for each person, i.e.:

        {
            [email]: ["SKILL_THAT_WAS_PREDICTED_TRUE"]
        }
        """
        if len(raw_stats) == 0:
            logger.warn("Received an empty set of raw stats; returning an empty result")
            return {}

        processed_data = ProcessedGitData(raw_stats)
        feature_vectors = processed_data.generate_feature_vectors()

        predictions = self._heuristic_model(feature_vectors)

        if existing_emails:
            return self._remap_prediction_emails(predictions, existing_emails)
        else:
            return predictions

    def _heuristic_model(self, feature_vectors: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Heuristic (rules-based) model used to predict whether or not someone has a skill.
        It works by looking at various stats derived from the commit logs of a git repo.
        In essence, if a person has a sufficient number of commits, over a sufficient period of time,
        with a sufficient number of changes, they are said to have that skill.

        @param feature_vectors  The feature vectors generated by ProcessedGitData
        @return The predictions -- a dictionary keyed by email mapping to a list of the skills that person has.
        """
        # First level of filtering: number of commits and period of time between oldest and latest commit
        df = feature_vectors[feature_vectors["commit"] > 1]
        df = df[df["commit_date_difference"] > 1]

        # Split the skills into 'small' and 'regular' skills.
        # This is done so that 'small' skills (e.g. shell scripting, Dockerfile modifications) can have a different
        # threshold for number of changes needed to 'have' the skill.
        small_skills_df, regular_skills_df = self._split_skills(df)

        # Second level of filtering: number of changes
        small_skills_df = small_skills_df[small_skills_df["change_count"] > 2]
        regular_skills_df = regular_skills_df[regular_skills_df["change_count"] > 500]

        result = (
            small_skills_df
                # Combine the split skills back together.
                .append(regular_skills_df)
                # Group by email so that we can get all of the skills for each person.
                .groupby("email")
                # Convert the skills for each person into a list (for API response purposes).
                # Note that this has the side benefit of dropping all of the other columns for us.
                .apply(lambda x: list(x["skill"]))
                # Convert the whole thing to a dict (again, for API response purposes).
                .to_dict()
        )

        return result

    def _split_skills(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split the skills into 'small' and 'regular' skills, so that we can have different cutoffs
        for number of changes required to have that skill.
        The reason we do this is because some 'small' skills, like shell scripting or Docker,
        are not conducive to large numbers of changes. As such, we lower the barrier for these skills
        in order to try and capture a broader skillset for people.
        """
        small_skill_filter = df["skill"].isin(SMALL_SKILLS)
        return (df[small_skill_filter], df[~small_skill_filter])

    def _remap_prediction_emails(self, predictions: PredictionsType, existing_emails: List[str]) -> PredictionsType:
        """
        Takes a list of existing emails (e.g. from the Skillhub backend database that were scraped from Jira) and
        uses them to remap the emails retrieved from the repos. This is necessary because some/a lot of people
        don't necessarily setup their git email to match their Jira email.
        """
        git_emails = list(predictions.keys())
        matching_existing_emails = self.email_matcher.find_matching_emails(git_emails, existing_emails)

        remapped_predictions = {}  # type: Dict[str, List[str]]

        for email, skills in predictions.items():
            existing_email = matching_existing_emails[email]

            if existing_email:
                remapped_predictions.setdefault(existing_email, [])
                remapped_predictions[existing_email] = list(set(remapped_predictions[existing_email] + skills))

        return remapped_predictions
