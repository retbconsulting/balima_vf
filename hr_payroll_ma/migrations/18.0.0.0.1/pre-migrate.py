from odoo import api, SUPERUSER_ID, Command
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.warning("Starting migration for hr employee tags ========================")
    cr.execute("""
        SELECT id, name, code, company_id FROM account_analytic_tag;
    """)
    tags = cr.fetchall()

    tag_to_account_map = {}
    #bl_plan = env['account.analytic.plan'].search([('name', '=', 'BL')], limit=1)

    for tag in tags:
        tag_id = tag[0]
        tag_name = tag[1]
        tag_code = tag[2]
        company_id = tag[3]

        account = env['account.analytic.account'].search([('name', '=', tag_name)], order='id asc', limit=1)

        """if not account:
            account = env['account.analytic.account'].create({
                'name': tag_name,
                'code': tag_code or '',
                'company_id': company_id,
                'plan_id': bl_plan.id,
            })"""

        tag_to_account_map[tag_id] = account.id

    tables_to_update = [
        'hr.employee',

    ]

    for table in tables_to_update:
        cr.execute(f"""
            SELECT id, analytic_tag_id FROM {table} WHERE analytic_tag_id IS NOT NULL;
        """)
        rows = cr.fetchall()

        for row in rows:
            record_id = row[0]
            old_tag_id = row[1]
            new_account_id = tag_to_account_map.get(old_tag_id)

            if new_account_id:
                cr.execute(f"""
                    UPDATE {table}
                    SET analytic_tag_id = %s
                    WHERE id = %s
                """, (new_account_id, record_id))
        # Log unmapped tag_ids
        cr.execute(f"""
            SELECT analytic_tag_id FROM {table}
            WHERE analytic_tag_id IS NOT NULL
            AND analytic_tag_id NOT IN %s;
        """, (tuple(tag_to_account_map.keys()),))
        missing_tags = cr.fetchall()
        if missing_tags:
            missing_ids = [str(r[0]) for r in missing_tags]
            _logger.warning(f"[Migration] {table}: Unmigrated analytic_tag_ids: {', '.join(missing_ids)}")

    cr.commit()

    print("Migration completed!")