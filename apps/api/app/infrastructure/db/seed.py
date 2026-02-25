from __future__ import annotations

import os
import uuid

from sqlalchemy import create_engine, text


STAGES_DATA = [
    {
        "title": "תכנון והיתרים",
        "order_index": 1,
        "description": "שלב התכנון וההיתרים הוא השלב הראשון והחשוב ביותר בבניית בית. בשלב זה יש להכין תוכניות אדריכליות, לקבל היתרי בנייה, ולבחור את הקבלן.",
        "tips": [
            {
                "type": "info",
                "content": "ודא שהתוכניות האדריכליות מאושרות על ידי הוועדה המקומית לפני תחילת העבודה.",
            },
            {
                "type": "warning",
                "content": "אל תתחיל עבודות ללא היתר בנייה תקף - זה עלול לגרום לקנסות כבדים ואף להריסת הבנייה.",
            },
            {
                "type": "recommendation",
                "content": "התייעץ עם אדריכל מנוסה שיכול לסייע בתכנון מיטבי של הבית.",
            },
        ],
        "checklist_items": [
            {"text": "הכנת תוכניות אדריכליות מפורטות", "is_critical": True},
            {"text": "קבלת היתר בנייה מהרשות המקומית", "is_critical": True},
            {"text": "בחירת קבלן ראשי מנוסה", "is_critical": True},
            {"text": "חתימה על חוזה בנייה מפורט", "is_critical": True},
            {"text": "ביטוח אחריות קבלן", "is_critical": False},
            {"text": "תכנון תקציב מפורט", "is_critical": False},
        ],
    },
    {
        "title": "עבודות עפר",
        "order_index": 2,
        "description": "שלב עבודות העפר כולל פינוי שטח, חפירה, מילוי וסלילת דרכים זמניות. זהו השלב שבו מתחילה הבנייה בפועל.",
        "tips": [
            {
                "type": "info",
                "content": "ודא שהקבלן מבצע בדיקת קרקע לפני תחילת החפירה.",
            },
            {
                "type": "warning",
                "content": "שימו לב למיקום תשתיות תת-קרקעיות (מים, חשמל, תקשורת) כדי למנוע נזקים.",
            },
            {
                "type": "recommendation",
                "content": "שמור על הקרקע העליונה (טופ סויל) לשימוש מאוחר יותר בגינה.",
            },
        ],
        "checklist_items": [
            {"text": "פינוי שטח וסילוק פסולת", "is_critical": True},
            {"text": "חפירה לפי התוכניות", "is_critical": True},
            {"text": "בדיקת קרקע וטיפול בקרקע בעייתית", "is_critical": True},
            {"text": "מילוי וסלילת דרכים זמניות", "is_critical": False},
            {"text": "התקנת גדר זמנית", "is_critical": False},
        ],
    },
    {
        "title": "יסודות",
        "order_index": 3,
        "description": "שלב היסודות הוא הבסיס לכל הבנייה. יסודות חזקים ויציבים הם קריטיים לבטיחות ולעמידות הבית.",
        "tips": [
            {
                "type": "warning",
                "content": "אל תתחיל שלבים נוספים לפני שהיסודות יבשו לחלוטין - זה עלול לגרום לסדקים.",
            },
            {
                "type": "info",
                "content": "ודא שהברזל ביסודות מונח לפי התקן ומוגן מפני קורוזיה.",
            },
            {
                "type": "recommendation",
                "content": "בצע בדיקת בטון (slump test) כדי לוודא איכות הבטון.",
            },
        ],
        "checklist_items": [
            {"text": "הנחת ברזל יסודות לפי התקן", "is_critical": True},
            {"text": "יציקת בטון יסודות", "is_critical": True},
            {"text": "ייבוש מלא של היסודות", "is_critical": True},
            {"text": "בידוד תרמי ביסודות", "is_critical": False},
            {"text": "איטום יסודות מפני לחות", "is_critical": True},
        ],
    },
    {
        "title": "מבנה שלד",
        "order_index": 4,
        "description": "שלב בניית השלד כולל את כל הקירות, העמודים, הקורות והרצפות. זהו השלד של הבית.",
        "tips": [
            {
                "type": "info",
                "content": "ודא שהקירות נבנים ישרים ואנכיים - זה ישפיע על כל הבנייה הבאה.",
            },
            {
                "type": "warning",
                "content": "בדוק את מיקום הפתחים (חלונות ודלתות) לפני יציקת הקירות.",
            },
            {
                "type": "recommendation",
                "content": "בצע בדיקות תקופתיות של איכות הבטון והברזל.",
            },
        ],
        "checklist_items": [
            {"text": "הקמת קירות שלד", "is_critical": True},
            {"text": "יציקת רצפות", "is_critical": True},
            {"text": "התקנת פתחים (חלונות ודלתות)", "is_critical": True},
            {"text": "בדיקת יישור ואנכיות", "is_critical": True},
            {"text": "ניקוי וסילוק פסולת", "is_critical": False},
        ],
    },
    {
        "title": "תשתיות - אינסטלציה וחשמל",
        "order_index": 5,
        "description": "שלב התשתיות כולל הנחת צנרת מים, ביוב, חשמל ותקשורת. חשוב לבצע זאת לפני טיח ובידוד.",
        "tips": [
            {
                "type": "warning",
                "content": "ודא שכל הצנרת והכבלים מוגנים מפני נזקים - תיקונים מאוחר יותר יקרים מאוד.",
            },
            {
                "type": "info",
                "content": "בצע בדיקת לחץ מים לפני סגירת הקירות.",
            },
            {
                "type": "recommendation",
                "content": "תכנן נקודות חשמל ותקשורת נוספות - קל יותר להוסיף עכשיו מאשר אחר כך.",
            },
        ],
        "checklist_items": [
            {"text": "הנחת צנרת מים קרים וחמים", "is_critical": True},
            {"text": "הנחת צנרת ביוב", "is_critical": True},
            {"text": "הנחת כבלי חשמל", "is_critical": True},
            {"text": "הנחת כבלי תקשורת", "is_critical": False},
            {"text": "בדיקת לחץ מים", "is_critical": True},
            {"text": "בדיקת חשמל", "is_critical": True},
        ],
    },
    {
        "title": "איטום",
        "order_index": 6,
        "description": "שלב האיטום הוא קריטי למניעת חדירת מים ולחות לבית. איטום לקוי עלול לגרום לנזקים כבדים.",
        "tips": [
            {
                "type": "warning",
                "content": "איטום לקוי הוא אחד הגורמים העיקריים לנזקים בבתים - אל תחסוך כאן.",
            },
            {
                "type": "info",
                "content": "ודא שהאיטום מבוצע בכל האזורים החשופים: גג, מרפסות, חדרי רחצה.",
            },
            {
                "type": "recommendation",
                "content": "בצע בדיקת איטום (בדיקת מים) לפני המשך הבנייה.",
            },
        ],
        "checklist_items": [
            {"text": "איטום גג", "is_critical": True},
            {"text": "איטום מרפסות", "is_critical": True},
            {"text": "איטום חדרי רחצה", "is_critical": True},
            {"text": "איטום קירות חיצוניים", "is_critical": True},
            {"text": "בדיקת איטום", "is_critical": True},
        ],
    },
    {
        "title": "ריצוף וטיח",
        "order_index": 7,
        "description": "שלב הריצוף והטיח נותן לבית את המראה הסופי. זה כולל הנחת ריצוף, טיח פנימי וחיצוני, ובידוד תרמי.",
        "tips": [
            {
                "type": "info",
                "content": "ודא שהריצוף מונח על משטח ישר ונקי.",
            },
            {
                "type": "recommendation",
                "content": "בחר חומרי ריצוף עמידים וקלים לתחזוקה.",
            },
            {
                "type": "warning",
                "content": "המתן לייבוש מלא של הטיח לפני צביעה או הדבקת אריחים.",
            },
        ],
        "checklist_items": [
            {"text": "הנחת ריצוף", "is_critical": True},
            {"text": "טיח פנימי", "is_critical": True},
            {"text": "טיח חיצוני", "is_critical": True},
            {"text": "בידוד תרמי", "is_critical": False},
            {"text": "השלמת עבודות גבס", "is_critical": False},
        ],
    },
    {
        "title": "גימור",
        "order_index": 8,
        "description": "שלב הגימור כולל את כל הפרטים הסופיים: צביעה, התקנת מטבח, ארונות, דלתות פנים, ועוד.",
        "tips": [
            {
                "type": "info",
                "content": "תכנן את סדר העבודות - מטבח וארונות לפני צביעה סופית.",
            },
            {
                "type": "recommendation",
                "content": "בחר חומרי גמר איכותיים - הם ישפיעו על המראה והעמידות לטווח הארוך.",
            },
            {
                "type": "warning",
                "content": "ודא שכל העבודות מבוצעות לפי התקן - במיוחד במטבח ובחדרי רחצה.",
            },
        ],
        "checklist_items": [
            {"text": "צביעה פנימית וחיצונית", "is_critical": True},
            {"text": "התקנת מטבח", "is_critical": True},
            {"text": "התקנת ארונות", "is_critical": False},
            {"text": "התקנת דלתות פנים", "is_critical": True},
            {"text": "התקנת חלונות", "is_critical": True},
            {"text": "השלמת עבודות חשמל (תאורה, שקעים)", "is_critical": True},
        ],
    },
    {
        "title": "ביקורת ואכלוס",
        "order_index": 9,
        "description": "השלב האחרון כולל ביקורת סופית, קבלת טופס 4, וסיום כל העבודות לפני האכלוס.",
        "tips": [
            {
                "type": "warning",
                "content": "אל תאכלס את הבית לפני קבלת טופס 4 - זה עלול לגרום לבעיות ביטוח ובעיות משפטיות.",
            },
            {
                "type": "info",
                "content": "בצע ביקורת יסודית של כל המערכות לפני האכלוס.",
            },
            {
                "type": "recommendation",
                "content": "שמור על כל המסמכים והאסמכתאות - תצטרך אותם בעתיד.",
            },
        ],
        "checklist_items": [
            {"text": "ביקורת סופית של כל המערכות", "is_critical": True},
            {"text": "קבלת טופס 4", "is_critical": True},
            {"text": "השלמת כל העבודות", "is_critical": True},
            {"text": "ניקיון יסודי", "is_critical": False},
            {"text": "העברת מפתחות", "is_critical": True},
        ],
    },
]


def seed_stages(database_url: str | None = None) -> None:
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL must be set to run seed script.")

    engine = create_engine(url)

    with engine.begin() as conn:
        # ננקה את הנתונים הקיימים ונזרע מחדש את שלבי הקטלוג
        conn.execute(text("DELETE FROM stage_check_items"))
        conn.execute(text("DELETE FROM stages"))

        for idx, stage in enumerate(sorted(STAGES_DATA, key=lambda s: s["order_index"]), start=1):
            slug = f"stage-{idx}"

            short_explanation = stage["description"]
            warnings = " ".join(
                tip["content"] for tip in stage["tips"] if tip.get("type") == "warning"
            )
            others = " ".join(
                tip["content"]
                for tip in stage["tips"]
                if tip.get("type") in {"info", "recommendation"}
            )

            stage_id = str(uuid.uuid4())
            conn.execute(
                text(
                    """
                    INSERT INTO stages (
                        id, slug, title, short_explanation,
                        common_mistakes, must_document, order_index
                    )
                    VALUES (:id, :slug, :title, :short_explanation,
                            :common_mistakes, :must_document, :order_index)
                    """
                ),
                {
                    "id": stage_id,
                    "slug": slug,
                    "title": stage["title"],
                    "short_explanation": short_explanation,
                    "common_mistakes": warnings,
                    "must_document": others,
                    "order_index": stage["order_index"],
                },
            )

            for order_index, item in enumerate(stage["checklist_items"], start=1):
                title = item["text"]
                description = "קריטי" if item.get("is_critical") else None
                conn.execute(
                    text(
                        """
                        INSERT INTO stage_check_items (
                            id, stage_id, title, description, order_index
                        )
                        VALUES (:id, :stage_id, :title, :description, :order_index)
                        """
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "stage_id": stage_id,
                        "title": title,
                        "description": description,
                        "order_index": order_index,
                    },
                )


if __name__ == "__main__":
    seed_stages()

