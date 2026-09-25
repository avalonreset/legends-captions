import unittest

from legends_captions.policy import apply_caption_policy, normalize_text


class CaptionPolicyTests(unittest.TestCase):
    def test_low_raw_normalizes_to_lora(self):
        result = apply_caption_policy(["low", "raw."])
        self.assertEqual(result.text, "LoRA.")
        self.assertEqual(result.decisions[0].category, "domain_term")

    def test_seedance_contextual_repair(self):
        self.assertEqual(
            normalize_text("it may not be as exacting 2.0,", uppercase=True),
            "IT MAY NOT BE AS EXCITING AS SEEDANCE 2.0,",
        )

    def test_what_does_this_unlock_repair(self):
        self.assertEqual(
            normalize_text("so what is this unlock?", uppercase=True),
            "SO WHAT DOES THIS UNLOCK?",
        )

    def test_sticking_to_30_repair(self):
        self.assertEqual(
            normalize_text("sticking the 30 frames a second makes more", uppercase=True),
            "STICKING TO 30 FRAMES A SECOND MAKES MORE",
        )

    def test_spoken_lora_letters_stay_highlightable(self):
        result = apply_caption_policy(["L", "O", "R", "A."])
        self.assertEqual(result.text, "L O R A.")
        self.assertTrue(all("spoken_acronym_letter" in token.flags for token in result.tokens))
        self.assertEqual(result.decisions[0].category, "spoken_acronym_timing")

    def test_joined_profanity_phrase_split(self):
        self.assertEqual(
            normalize_text("everyone needs to calm the fuckdown", uppercase=True),
            "EVERYONE NEEDS TO CALM THE FUCK DOWN",
        )


if __name__ == "__main__":
    unittest.main()

