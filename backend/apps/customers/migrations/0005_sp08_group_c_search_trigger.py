"""
Custom migration to create a PostgreSQL trigger that auto-populates
the search_vector column on Customer INSERT / UPDATE.
"""

from django.db import migrations


# SQL to create the trigger function and attach it
FORWARD_SQL = """
CREATE OR REPLACE FUNCTION update_customer_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.customer_code, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.first_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.last_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.display_name, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.business_name, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.phone, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.mobile, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.organization_name, '')), 'D') ||
        setweight(to_tsvector('english', COALESCE(NEW.notes, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_customer_search_vector ON customers_customer;

CREATE TRIGGER trg_customer_search_vector
    BEFORE INSERT OR UPDATE ON customers_customer
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_search_vector();
"""

# SQL to remove the trigger and function on reverse
REVERSE_SQL = """
DROP TRIGGER IF EXISTS trg_customer_search_vector ON customers_customer;
DROP FUNCTION IF EXISTS update_customer_search_vector();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0004_sp08_group_c"),
    ]

    operations = [
        migrations.RunSQL(
            sql=FORWARD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]
