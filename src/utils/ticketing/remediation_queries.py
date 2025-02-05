import jinja2

CREATE_REMEDIATION_QUEUE = jinja2.Template('''
mutation {
  create_remediation_queue(
    title: "{{title}}"
    cron: "0 21 * * *"
    description: "{{title}}"
    max_concurrent_opened_tickets: {{max_concurrent_opened_tickets}}
    state: {{state}}
    endpoint_type: TICKET
    ticket_provider_id: "{{ticket_provider_id}}"
    filters_config: {{filters_config}}
    value_mapping: "{{value_mapping}}"
  ) {
    remediation_queue {
        id
        field_mapping {
            id
            value_mapping
        }
    }
  }
}
''')

DELETE_REMEDIATION_QUEUE = jinja2.Template('''
mutation {
  delete_remediation_queue(id: "{{id}}") {
    ok
  }
}
''')
