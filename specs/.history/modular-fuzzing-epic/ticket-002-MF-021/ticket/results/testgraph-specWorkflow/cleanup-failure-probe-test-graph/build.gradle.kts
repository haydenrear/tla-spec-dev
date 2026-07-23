plugins {
    id("com.hayden.testgraphsdk.graph")
}

validationGraph {
    sourcesDir("sources")

    testGraph("cleanupFailureProbe") {
        node("sources/tla_spec_dev_cli_install.py")
        node("sources/spec_workflow_create_repo.py")
        node("sources/spec_workflow_force_failure.py")
        node("sources/spec_workflow_cleanup.py").dependsOn("spec.workflow.force_failure")
    }
}
