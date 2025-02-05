import jinja2

GET_TICKET_MANAGERS_QUERY = jinja2.Template('''
query {
    ticket_managers( providers_query_context:  CREATE_TICKET ) {
      type
      providers {
        id
        is_installed
        known_identifier
        external_identifier
        oauth_client_id
      }
    }
}
''')

GET_ENDPOINT_KEYS_QUERY = jinja2.Template('''
fragment fieldInputFragment on FieldInput {
  field_name
  default_value
  field_input_type
  options {
    values {
      id
      name
    }
  }
}

query {
  endpoint_keys(
    ticket_provider_id: "{{ticket_provider_id}}"
    selected_keys: "{{selected_keys}}"
    {{field_mapping_id}}
  ) {
    is_final
    fields_sections {
      rows {
        fields {
          ...fieldInputFragment
        }
      }
    }
  }
}''')


GET_QUERY_FIELDS_QUERY =  jinja2.Template("""
    query get_query_fields {
      get_query_fields(
        ticket_provider_id: "{{ticket_provider_id}}"
        field_name: "{{field_name}}"
        params: "{{params}}"
      ) {
        values {
          id
          name
        }
      }
    }
""")

GET_ENDPOINT_FIELDS_QUERY = jinja2.Template("""
fragment fieldInputFragment on FieldInput {
  field_name
  required
  default_value
  options {
    values {
      id
      name
    }
  }
}

fragment mapperFieldInputFragment on MapperRowField {
  field_name
  default_value
  options {
    values {
      id
      name
    }
  }
  query_data
}

query {
  endpoint_fields(
    {{filters_config}}
    {{field_mapping_id}}
    ticket_provider_id: "{{ticket_provider_id}}"
    selected_keys: "{{selected_keys}}"
    endpoint_fields_context: "CREATE_TICKET"
  ) {
    fields_sections {
      rows {
        fields {
          mapping_data {
            rows {
              field_from {
                ...mapperFieldInputFragment
              }
              field_to {
                ...mapperFieldInputFragment
              }
            }
          }
          ...fieldInputFragment
        }
      }
    }
  }
}
""")

MUTATION_OPEN_TICKET = jinja2.Template('''
mutation {
  open_ticket(
    filters_config: {filtersjson: "{\\"field\\":\\"id\\",\\"condition\\":\\"in\\", \\"value\\": [{{finding_id}}]}"}
    ticket_provider_id: "{{ticket_provider_id}}"
    value_mapping: "{{value_mapping}}"
  ) {
    ticket {
        id
        external_id
        link
        assignee
        status
    }
  }
}
''')
