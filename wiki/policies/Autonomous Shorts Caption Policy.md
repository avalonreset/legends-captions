---
type: policy
status: active
created: 2026-06-21
updated: 2026-06-21
tags:
  - captions
  - shorts
  - timing
  - overlays
  - qa
---

# Autonomous Shorts Caption Policy

Use this policy when Ultimate Captions is preparing captions or on-screen text for an autonomous YouTube Short.

## Bottom Speech Caption Lane

- Bottom captions are speech captions. They should follow the approved Ultimate Captions look: all caps, bold high-contrast type, white inactive words, cyan/blue active word, maximum two lines, and lower-quarter placement.
- Rebuild bottom captions from the exact final render clock after every cut, retime, or gap compression.
- Known edit boundaries are caption group boundaries. Do not let a bottom speech-caption group continue across a hard cut just to carry one or two leftover words from the previous scene.
- If a hard cut happens, finish the outgoing caption at the cut and start a fresh group for the next scene unless there is a documented creative exception.
- The final caption manifest should report zero caption events crossing known cut boundaries and zero invalid or negative-duration ASS events.
- Caption text must cover audible retained words. If a retained word is audible, it needs to be captioned intentionally or the edit boundary needs repair.

## Upper Editorial Caption Lane

- Upper text is not a duplicate transcript lane. It is for short topic markers, framing prompts, and payoff markers.
- Default upper-caption style for Shorts is static bright yellow text, near the upper quarter of the 9:16 frame.
- Avoid muddy mustard. The intended direction is high-visibility Hormozi-style yellow.
- Do not use per-word active highlights on upper captions by default. Moving upper highlights compete with bottom speech captions.
- Keep upper captions brief and non-redundant with bottom speech. Good examples include `CONTROL CLAUDE CODE FROM YOUR PHONE`, `OPEN CODE ON MOBILE`, `REVIEW AND REPLY`, `JUMP BETWEEN CHATS`, and `YOU SHOULD USE IT`.
- Remove the previous upper caption before the next one appears. Sloppy overlap between upper captions is a reject condition.

## Final Word And Tail

- The final bottom caption must include the actual final spoken payoff word or phrase.
- The Short should end almost immediately after the final spoken word. Default target is about three frames after the final word on a 60 fps render unless the editor documents a deliberate visual hold.
- If the final output hangs for a second or more after speech ends, reject the render for tail trim.

## QA Evidence

Every autonomous Shorts caption package should preserve:

- final output path and duration;
- known cut-boundary list;
- bottom caption manifest with cut-crossing count and invalid-event count;
- upper caption manifest with text, timing, and purpose;
- proof frames at the opening, each hard cut, a middle beat, and the final word/tail;
- final-audio ASR comparison against intended display text for high-impact terms.

## Revision Learning

After a Short is reviewed, feed accepted caption feedback back into [[Revision Learning Policy]].

- Repeated caption, timing, layout, upper-text, or tail-trim feedback should become policy, config, tests, or QA gates.
- One-off subjective calls can be saved as examples, but should not become global defaults unless the user repeats or explicitly frames them as policy.
- The success metric is fewer versions per usable Short. If a known failure recurs, the caption package runner should fail earlier or choose the better default automatically.
