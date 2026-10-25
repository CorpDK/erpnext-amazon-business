frappe.pages["amazon-business-connect"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Amazon Business Connect"),
		single_column: true,
	});

	page.main.html(`
		<div class="amazon-business-connect-shell">
			<p class="text-muted">${__(
				"Connect Amazon Business storefronts per company. OAuth opens in a new window; relay mode polls pending tokens automatically."
			)}</p>
			<div class="form-group">
				<label>${__("Company")}</label>
				<input type="text" class="form-control" id="ab-connect-company" placeholder="Company name" />
			</div>
			<div class="form-group">
				<label>${__("Storefront")}</label>
				<input type="text" class="form-control" id="ab-connect-storefront" placeholder="amazon.in" />
			</div>
			<button class="btn btn-primary" id="ab-connect-start">${__("Connect")}</button>
			<button class="btn btn-default" id="ab-connect-pull">${__("Pull relay OAuth")}</button>
			<pre class="ab-connect-status" id="ab-connect-status"></pre>
		</div>
	`);

	const status = (msg) => {
		wrapper.querySelector("#ab-connect-status").textContent = msg;
	};

	wrapper.querySelector("#ab-connect-start").addEventListener("click", () => {
		const company = wrapper.querySelector("#ab-connect-company").value;
		const storefront = wrapper.querySelector("#ab-connect-storefront").value;
		frappe.call({
			method: "erpnext_amazon_business.relay.desk.get_connect_url",
			args: { company, storefront },
			callback: (r) => {
				if (r.message?.url) {
					window.open(r.message.url, "_blank", "noopener");
					status(__("Opened OAuth window ({0})", [r.message.connection_mode]));
				}
			},
		});
	});

	wrapper.querySelector("#ab-connect-pull").addEventListener("click", () => {
		const company = wrapper.querySelector("#ab-connect-company").value;
		const storefront = wrapper.querySelector("#ab-connect-storefront").value;
		frappe.call({
			method: "erpnext_amazon_business.relay.desk.trigger_oauth_pull",
			args: { company, storefront },
			callback: (r) => {
				status(
					r.message?.handled
						? __("Relay OAuth token applied.")
						: __("No READY oauthPending for this pair.")
				);
			},
		});
	});

	frappe.realtime.on("amazon_business_relay", (data) => {
		status(JSON.stringify(data));
	});
};
