plugins {
    id("com.hayden.testgraphsdk.graph")
}

validationGraph {
    sourcesDir("sources")

    testGraph("specWorkflow") {
        node("sources/tla_spec_dev_cli_install.py")
        node("sources/spec_workflow_create_repo.py")
        node("sources/spec_workflow_start_ticket.py")
        node("sources/spec_workflow_complete_ticket.py")
        node("sources/spec_workflow_spec_units.py")
        node("sources/spec_workflow_close_ticket.py")
        node("sources/spec_workflow_failure_cleanup_probe.py")
        node("sources/spec_workflow_cleanup.py")
        // G-12: the reference adapters must import where an adopter runs them,
        // asserted where the environment cannot supply the answer. Its unit
        // test was green for a property of the operator's machine.
        node("sources/reference_adapters_resolve.py")
    }

    testGraph("cliWorkflow") {
        node("sources/tla_spec_dev_cli_install.py")
        node("sources/tla_spec_dev_cli_help.py")
    }

    testGraph("effectProviderExamples") {
        node("sources/effect_provider_examples.py")
    }
}
