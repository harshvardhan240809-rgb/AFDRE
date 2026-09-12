# Inventory Incident Playbook

If inventory service health drops, restart the service and ensure data consistency before allowing order retries to resume. Stale reads should be treated as degraded until inventory state is confirmed.
