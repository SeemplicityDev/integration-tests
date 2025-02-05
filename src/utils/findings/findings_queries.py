import jinja2

GET_PLAIN_FINDINGS_QUERY = jinja2.Template('''
fragment ActualStatus on FindingsView {
  actual_status {
    category
  }
}

fragment Tickets on FindingsView {
  tickets {
    edges {
      node {
        id
        status
        external_id
        created_by_remediation_queue_id
    }
    }
  }
}

query  {
  findings: findings_view
    {{filters_config}}
  {
    edges {
      node {
        id
        id_int
        title
        score
        remediation_sub_phase
        cloud_account
        cloud_account_friendly_name
        cloud_provider
        resource_name
        resource_type
        sla_status
        age
        datasource_tags_values
        source
        ...Tickets
        ...ActualStatus
      }
    }
  }
}
''')
