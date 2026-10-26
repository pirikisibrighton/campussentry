# CampusSentry NLP: Annotation Guideline (v1.0)

Every report gets: **one category, one severity, one language label, and entity spans.**

## 1. Category (pick one)
Fire | Medical Emergency | Theft/Break-in | Harassment/Assault | Infrastructure Fault | Road Accident | Service Outage | Other/Non-urgent

- Visibly broken = **Infrastructure Fault**. Service simply off = **Service Outage**.
- If a report fits two categories, pick the one that is the most urgent.
- Slow or unreliable Wi-Fi counts as Service Outage (usually Low severity).

## 2. Severity (pick one)
- **High:** danger to life or safety now, or actively getting worse.
- **Medium:** real damage, loss or disruption, nobody in immediate danger.
- **Low:** minor, routine, can wait, or already resolved with no injuries.

Rules: label the worst credible reading; category does not decide severity; whole-complex or exam-time outages are Medium; theft in progress is High, theft already discovered is Medium.

## 3. Language (pick one)
- **English:** entirely English.
- **Mixed:** English and Shona phrases in the same report.
- **Shona:** entirely Shona. Place names and common loanwords do not count.

## 4. Entities
| Type | Tag | Do not tag |
|---|---|---|
| LOCATION | library, P complex, A1.2, boom gate | "outside", "everywhere" |
| DATE_TIME | last night, at 3pm, since morning, now | times that are not stated |
| ASSET | laptop, router, pipe, generator, water, Wi-Fi | the whole incident |
| PERSON_ROLE | student, lecturer, security guard | personal names |

Rules: tag the smallest span; rooms and complexes are separate LOCATION spans; never tag personal names.
Services such as water, electricity, power, lights, Wi-Fi and internet are tagged ASSET when they are the subject of the problem. Tag all spelling variants the same way (Wi-Fi, wifi, WiFi, internet).

## 5. Worked examples

**Example 1**
> "Smoke coming from room C2.1 in C complex, please come quickly."
- Category: Fire | Severity: High | Language: English
- Entities: C2.1 (LOCATION), C complex (LOCATION)

**Example 2**
> "My laptop was stolen from A1.2 last night while we were at class."
- Category: Theft/Break-in | Severity: Medium | Language: English
- Entities: laptop (ASSET), A1.2 (LOCATION), last night (DATE_TIME)

**Example 3**
> "No Wi-Fi in K complex since yesterday."
- Category: Service Outage | Severity: Medium | Language: English
- Entities: Wi-Fi (ASSET), K complex (LOCATION), since yesterday (DATE_TIME)

**Example 4 (Mixed, to be checked by a Shona speaker)**
> "Pane moto kuC complex, please send security now."
- Category: Fire | Severity: High | Language: Mixed
- Entities: C complex (LOCATION), security (PERSON_ROLE), now (DATE_TIME)

**Example 5 (resolved incident)**
> "Small fire in the bin outside the dining hall, a cleaner put it out, nobody hurt."
- Category: Fire | Severity: Low | Language: English
- Entities: dining hall (LOCATION), cleaner (PERSON_ROLE)

- Resolved or contained (culprit caught, fire out, no injuries): Low.
- Broken item in a student's room that stops normal use (window, lock, light, bed): Medium. Purely cosmetic or minor: Low.
- Hazards that can spread or injure (spreading flood, hot-water or electrical fault, any fire still burning, vehicle crash where injury is not ruled out): High, even if described as small.
- Vague illness ("someone is sick") with no sign of danger: Medium. Collapse, heavy bleeding, vomiting blood or unresponsive: High.