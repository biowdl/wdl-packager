version 1.0

import "file://gatk-variantcalling/gatk-variantcalling.wdl" as variantcalling

task echo {
    input {
        String text
    }
    command {
        echo ~{text}
    }
    output {
        String out = stdout()
    }
    runtime {
        docker: "debian:buster-slim"
    }
}