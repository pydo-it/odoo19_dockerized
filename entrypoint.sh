#!/bin/bash
set -e

# Load password from file if provided
if [ -n "$PASSWORD_FILE" ] && [ -f "$PASSWORD_FILE" ]; then
    PASSWORD="$(< "$PASSWORD_FILE")"
fi

# Database connection defaults
HOST="${ODOO_HOST:-db}"
PORT="${ODOO_PORT:-5432}"
USER="${POSTGRES_USER:-odoo}"
PASSWORD="${POSTGRES_PASSWORD:-odoo}"

DB_ARGS=()

function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*${param}\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*${param}\s*=" "$ODOO_RC" | cut -d '=' -f2 | tr -d ' "\n\r')
    fi
    DB_ARGS+=("--${param}" "${value}")
}

check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            wait-for-psql.py "${DB_ARGS[@]}" --timeout=30
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        wait-for-psql.py "${DB_ARGS[@]}" --timeout=30
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
