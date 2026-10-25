app_name = "erpnext_amazon_business"
app_title = "ERPNext Amazon Business"
app_publisher = "CorpDK"
app_description = "Amazon Business buyer integration for ERPNext"
app_email = "ops@corpdk.local"
app_license = "GPL-3.0-or-later"

required_apps = ["erpnext"]

add_to_apps_screen = [
	{
		"name": app_name,
		"title": app_title,
		"route": "/app/amazon-business",
		"has_permission": "erpnext_amazon_business.permissions.has_app_permission",
	},
]

before_install = "erpnext_amazon_business.patches.check_version_compatibility.execute"
before_migrate = "erpnext_amazon_business.patches.check_version_compatibility.execute"

after_install = "erpnext_amazon_business.install.after_install"
after_migrate = "erpnext_amazon_business.install.after_migrate"

scheduler_events = {
	"cron": {
		"*/5 * * * *": ["erpnext_amazon_business.relay.worker.run_relay_worker_cycle"],
	},
}

fixtures = [
	{
		"dt": "Amazon Business Storefront",
		"filters": [
			[
				"storefront",
				"in",
				[
					"amazon.com",
					"amazon.ca",
					"amazon.com.mx",
					"amazon.co.uk",
					"amazon.de",
					"amazon.fr",
					"amazon.it",
					"amazon.es",
					"amazon.in",
					"amazon.co.jp",
					"amazon.com.au",
				],
			]
		],
	},
]
