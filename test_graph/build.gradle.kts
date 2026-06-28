plugins {
    id("com.hayden.testgraphsdk.graph")
}

validationGraph {
    sourcesDir("sources")

    testGraph("specWorkflow") {
        node("sources/spec_workflow_create_repo.py")
        node("sources/spec_workflow_start_ticket.py")
        node("sources/spec_workflow_complete_ticket.py")
        node("sources/spec_workflow_close_ticket.py")
        node("sources/spec_workflow_cleanup.py")
    }

    testGraph("cliWorkflow") {
        node("sources/tla_spec_dev_cli_install.py")
        node("sources/tla_spec_dev_cli_help.py")
    }
}
