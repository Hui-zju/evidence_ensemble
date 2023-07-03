import json
import pandas as pd


def export_gene():
    file_path = r"\\bmi-fs\Data.Common\Chenh\data\terminology\Oncokb\oncokb_curated_gene.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        variant = json.load(f)
    df = pd.DataFrame(variant)
    df.to_excel("证据库.xlsx", sheet_name='基因概要', index=False)


def export_variant():
    file_path = r"oncokb_evidence.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        evidences = json.load(f)
    mutationSummary = []
    for evidence in evidences:
        gene = evidence['gene']
        variant = evidence['variant']
        knownEffect = evidence['evidence']['mutationEffect']['knownEffect']
        mutationEffect = evidence['evidence']['mutationEffect']['description']
        pmids = ", ".join(evidence['evidence']['mutationEffect']['citations']['pmids'])
        variantSummary = evidence['evidence']['variantSummary']
        mutationSummary.append({'gene': gene, 'variant': variant, 'variantSummary': variantSummary,
                                'knownEffect': knownEffect,
                                'mutationEffect': mutationEffect, 'pmids': pmids})
    df = pd.DataFrame(mutationSummary)
    writer = pd.ExcelWriter(r"证据库.xlsx", mode="a", engine="openpyxl")
    df.to_excel(writer, sheet_name='变异概要', index=False)
    writer.save()
    writer.close()


def export_treatment():
    file_path = r"oncokb_evidence.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        evidences = json.load(f)
    treatments = []
    for evidence in evidences:
        query_gene = evidence['gene']
        query_variant = evidence['variant']
        implications = evidence['evidence']['treatments']
        for implication in implications:
            variant = " ,".join(implication['alterations'])
            ncitCode = " + ".join([drug['ncitCode'] for drug in implication['drugs']])
            drugName = " + ".join([drug['drugName'] for drug in implication['drugs']])
            level = implication['level']
            fdaLevel = implication['fdaLevel']
            AssociatedCancerTypeId = implication['levelAssociatedCancerType']['id']
            AssociatedCancerType = implication['levelAssociatedCancerType']['name']
            AssociatedCancerTissue = implication['levelAssociatedCancerType']['tissue']
            pmids = ", ".join(implication['pmids'])
            description = implication['description']

            treatments.append({'query_gene': query_gene, 'query_variant': query_variant, 'variant': variant, 'ncitCode': ncitCode,
                            'drugName': drugName, 'level': level, 'fdaLevel': fdaLevel,
                            'AssociatedCancerTypeId': AssociatedCancerTypeId,
                            'AssociatedCancerType': AssociatedCancerType,
                            'AssociatedCancerTissue': AssociatedCancerTissue,
                            'pmids': pmids, 'description': description})
    df = pd.DataFrame(treatments)
    writer = pd.ExcelWriter(r"证据库.xlsx", mode="a", engine="openpyxl")
    df.to_excel(writer, sheet_name='治疗证据', index=False)
    writer.save()
    writer.close()


def export_diagnostic():
    file_path = r"oncokb_evidence.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        evidences = json.load(f)
    diagnostics = []
    for evidence in evidences:
        query_gene = evidence['gene']
        query_variant = evidence['variant']
        implications = evidence['evidence']['diagnosticImplications']
        for implication in implications:
            variant = " ,".join(implication['alterations'])
            level = implication['levelOfEvidence']
            AssociatedCancerType = implication['tumorType']['name']
            AssociatedCancerTissue = implication['tumorType']['tissue']
            pmids = ", ".join(implication['pmids'])
            description = implication['description']

            diagnostics.append({'query_gene': query_gene, 'query_variant': query_variant, 'variant': variant,
                            'level': level, 'AssociatedCancerType': AssociatedCancerType,
                            'AssociatedCancerTissue': AssociatedCancerTissue,
                            'pmids': pmids, 'description': description})
    df = pd.DataFrame(diagnostics)
    writer = pd.ExcelWriter(r"证据库.xlsx", mode="a", engine="openpyxl")
    df.to_excel(writer, sheet_name='诊断证据', index=False)
    writer.save()
    writer.close()


def export_prognostic():
    file_path = r"oncokb_evidence.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        evidences = json.load(f)
    prognostics = []
    for evidence in evidences:
        query_gene = evidence['gene']
        query_variant = evidence['variant']
        implications = evidence['evidence']['prognosticImplications']
        for implication in implications:
            variant = " ,".join(implication['alterations'])
            level = implication['levelOfEvidence']
            AssociatedCancerType = implication['tumorType']['name']
            AssociatedCancerTissue = implication['tumorType']['tissue']
            pmids = ", ".join(implication['pmids'])
            description = implication['description']

            prognostics.append({'query_gene': query_gene, 'query_variant': query_variant, 'variant': variant,
                                'level': level, 'AssociatedCancerType': AssociatedCancerType,
                                'AssociatedCancerTissue': AssociatedCancerTissue,
                                'pmids': pmids, 'description': description})
    df = pd.DataFrame(prognostics)
    writer = pd.ExcelWriter(r"证据库.xlsx", mode="a", engine="openpyxl")
    df.to_excel(writer, sheet_name='预后证据', index=False)
    writer.save()
    writer.close()


if __name__ == '__main__':
    export_gene()
    export_variant()
    export_treatment()
    export_diagnostic()
    export_prognostic()

