# Payment Failover SOP

When the primary payment gateway becomes unavailable, first route new payment traffic to the backup gateway if capacity is available. Queue failed transactions and validate the backup gateway health before resuming retries. Track transaction consistency and avoid applying additional retry pressure until the database remains healthy.
