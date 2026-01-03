"""Application constants."""

# User roles
ROLE_SUPER_ADMIN = "super_admin"
ROLE_AGENCY_ADMIN = "agency_admin"
ROLE_AGENCY_MEMBER = "agency_member"
ROLE_CLIENT = "client"

ROLES = [ROLE_SUPER_ADMIN, ROLE_AGENCY_ADMIN, ROLE_AGENCY_MEMBER, ROLE_CLIENT]

# Document statuses
STATUS_DRAFT = "draft"
STATUS_GENERATING = "generating"
STATUS_READY = "ready"
STATUS_DISTRIBUTED = "distributed"
STATUS_FAILED = "failed"

DOCUMENT_STATUSES = [STATUS_DRAFT, STATUS_GENERATING, STATUS_READY, STATUS_DISTRIBUTED, STATUS_FAILED]

# Generation job statuses
JOB_PENDING = "pending"
JOB_RESEARCHING = "researching"
JOB_WRITING = "writing"
JOB_RENDERING = "rendering"
JOB_COMPLETED = "completed"
JOB_FAILED = "failed"

JOB_STATUSES = [JOB_PENDING, JOB_RESEARCHING, JOB_WRITING, JOB_RENDERING, JOB_COMPLETED, JOB_FAILED]

# Scheduled content statuses
SCHEDULE_PENDING = "pending"
SCHEDULE_PROCESSING = "processing"
SCHEDULE_COMPLETED = "completed"
SCHEDULE_FAILED = "failed"
SCHEDULE_CANCELED = "canceled"

SCHEDULE_STATUSES = [SCHEDULE_PENDING, SCHEDULE_PROCESSING, SCHEDULE_COMPLETED, SCHEDULE_FAILED, SCHEDULE_CANCELED]

# Content tones
TONES = ["professional", "conversational", "authoritative", "friendly", "formal"]

# Distribution platforms
PLATFORMS = ["linkedin", "facebook", "twitter", "google_business"]

# File limits
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_CSV_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# Document retention (days)
DOCUMENT_RETENTION_DAYS = 1095  # 3 years
SOFT_DELETE_GRACE_PERIOD_DAYS = 30
