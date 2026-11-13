#!/usr/bin/env bash
# Stand up a local Drupal 11 site in DDEV, apply the Strictly recipe and load the dataset.
#
#   scripts/drupal-local.sh setup     # ddev config + start, composer create-project, contrib modules, drush site:install
#   scripts/drupal-local.sh apply     # drush recipe recipes/strictly, then migrate the whole dataset (data/package)
#   scripts/drupal-local.sh update    # re-run the migrations with --update after a dataset rebuild
#   scripts/drupal-local.sh status    # node counts per bundle and the migrate status table
#   scripts/drupal-local.sh reset     # drop the site database and site:install again (recipe must be re-applied)
#
# The DDEV project root is the repository root, so inside the web container the dataset is at
# /var/www/html/data/package and the recipe at /var/www/html/recipes/strictly (the paths the migrations use).
set -euo pipefail
cd "$(dirname "$0")/.."
export DDEV_NONINTERACTIVE=true   # never block on a DDEV confirmation prompt (e.g. when run from CI or a background shell)

case "${1:-}" in
  setup)
    if [ ! -f .ddev/config.yaml ]; then
      ddev config --project-name=strictly --project-type=drupal11 --docroot=drupal/web --composer-root=drupal \
                  --php-version=8.3 --database=mariadb:10.11 --disable-settings-management=false
    fi
    ddev start -y
    if [ ! -f drupal/composer.json ]; then
      ddev composer create-project drupal/recommended-project:^11.2 --no-interaction
    fi
    ddev composer require --no-interaction -W drush/drush:^13 drupal/migrate_plus:^6 drupal/migrate_tools:^6 drupal/migrate_source_csv:^3
    ddev drush site:install minimal -y --account-pass=admin --site-name="Strictly Come Dancing results"
    echo "Drupal is up: $(ddev describe -j | python3 -c 'import json,sys; print(json.load(sys.stdin)["raw"]["primary_url"])')  (admin / admin)"
    ;;
  apply)
    ddev drush recipe /var/www/html/recipes/strictly
    ddev drush cache:rebuild
    ddev drush migrate:import --group=strictly
    "$0" status
    ;;
  update)
    ddev drush cache:rebuild
    ddev drush migrate:import --group=strictly --update
    "$0" status
    ;;
  status)
    ddev drush sql:query "SELECT type, COUNT(*) AS nodes FROM node_field_data GROUP BY type ORDER BY type"
    ddev drush sql:query "SELECT vid, COUNT(*) AS terms FROM taxonomy_term_field_data GROUP BY vid ORDER BY vid"
    ddev drush migrate:status --group=strictly
    ;;
  reset)
    ddev drush sql:drop -y
    ddev drush site:install minimal -y --account-pass=admin --site-name="Strictly Come Dancing results"
    ;;
  *)
    sed -n '2,12p' "$0"; exit 1 ;;
esac
