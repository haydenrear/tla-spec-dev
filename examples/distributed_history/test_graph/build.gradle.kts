plugins {
    id("com.hayden.testgraphsdk.graph")
}

validationGraph {
    sourcesDir("sources")

    testGraph("ecommerceExternal") {
        node("sources/deploy_ecommerce.py")
        node("sources/run_external_cases.py")
        node("sources/collect_evidence.py")
        node("sources/cleanup_ecommerce.py")
    }
}
