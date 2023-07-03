from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import pandas as pd
import json
import time
import os
import re
import argparse
import requests
from urllib.parse import urljoin
from hgvslib.pHGVS import pHGVS

# note1: copyNumber AMPLIFICATION = gain, DELETION = LOSS
# example1： APC Deletion Defined as copy number loss resulting in partial or whole deletion of the APC gene.
# note2： structuralVariantType including DELETION all equal fusion, returned mutationEffect include Truncating Mutations
# example2：ALDH2 Truncating Mutations Defined as nonsense, frameshift, or splice-site mutations within the ALDH2
# gene that are predicted to shorten the coding sequence of gene.
# note3： for structuralVariant， isFunctionalFusion = true is necessary
# note4: use NFE2L2 and inframe_deletion to query, get mutationEffect about "NFE2L2 Exon 2 in-frame deletions", but
# not get "NFE2L2 Exon 2 in-frame deletions"
api_url = {
    # hugoSymbol, copyNameAlterationType: [AMPLIFICATION, DELETION, GAIN, LOSS]
    "copyNumberAlterations": "https://www.oncokb.org/api/v1/annotate/copyNumberAlterations",
    # genomicLocation
    "byGenomicChange": "https://www.oncokb.org/api/v1/annotate/mutations/byGenomicChange",
    # hgvsg
    "byHGVSg": "https://www.oncokb.org/api/v1/annotate/mutations/byHGVSg",
    # hugoSymbol, alteration, consequence, proteinStart, proteinEnd, consequence: [feature_truncation,
    # frameshift_variant,inframe_deletion,inframe_insertion,start_lost,
    # missense_variant, splice_region_variant,stop_gained, intron_variant]
    "byProteinChange": "https://www.oncokb.org/api/v1/annotate/mutations/byProteinChange",
    # hugoSymbolA, hugoSymbolB, structuralVariantType:[DELETION, TRANSLOCATION, DUPLICATION, INSERTION,
    # INVERSION, FUSION, UNKNOWN], isFunctionalFusion
    "structuralVariants": "https://www.oncokb.org/api/v1/annotate/structuralVariants",
}


def get_oncokb_curated_variant_by_selenium():
    def get_genes_variant(gene_list):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        oncokb_variants = []
        for gene in gene_list:
            time.sleep(1)
            url = "https://www.oncokb.org/gene/" + gene + "#tab=Biological"
            driver.get(url)
            # WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "rt-tbody")))
            rows = [i for i in driver.find_elements_by_xpath("//div[@class='rt-tbody']/div/div")]
            variant_list = []
            for row in rows:
                # variant_list.append([i.text for i in row.find_elements_by_css_selector('div') if i.text])
                variant_list.append([i.text for i in row.find_elements_by_xpath('div') if i.text])
                # choose_class = row.find_element_by_class_name('fa fa-book')
                # webdriver.ActionChains(row).move_to_element(choose_class).perform()
            variant_list = [[gene] + variant for variant in variant_list]
            oncokb_variants += variant_list

        header = ['Gene', 'Alteration', 'Oncogenic', 'Mutation Effect']
        # header = [i.text for i in driver.find_elements_by_xpath("//div[@class='rt-thead -header']/div/div/div/span")]
        df = pd.DataFrame(oncokb_variants, columns=header)
        return df

    file_path = r"\\bmi-fs\Data.Common\Chenh\data\terminology\Oncokb\oncokb_curated_gene.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        variant = json.load(f)
    gene_list = [row['hugoSymbol'] for row in variant]
    df = get_genes_variant(gene_list)
    return df


def get_oncokb_evidence_by_api(module, parameters):
    headers = {'Authorization': 'Bearer {token}'.format(token="6b718457-5a3f-4a2a-bd2c-5c657909e0a4"),
               "accept": 'application/json'}
    r = requests.get(api_url[module], timeout=20, params=parameters, headers=headers)
    datas = json.loads(r.content)
    # print(json.dumps(datas, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))
    return datas


if __name__ == '__main__':
    # df = get_oncokb_curated_variant_by_selenium()
    # df.to_csv("datas.csv", index=False)
    # get_oncokb_evidence_by_api()
    df = pd.read_csv("datas.csv")
    genes = list(df["Gene"])
    alterations = list(df["Alteration"])
    oncokb_evidence = []
    i = 0
    for gene, alteration in zip(genes, alterations):
        i += 1
        print(i)
        if pHGVS("p." + alteration).type != "?":
            query = "byProteinChange"
            parameters = {'hugoSymbol': gene, 'alteration': alteration}
            evidence = get_oncokb_evidence_by_api(query, parameters)
        elif alteration in ["Fusions"]:
            query = "structuralVariants"
            alias = {"Fusions": "FUSION", "Deletion": "DELETION"}
            parameters = {'hugoSymbolA': gene, 'structuralVariantType': alias[alteration], 'isFunctionalFusion': 'true'}
            evidence = get_oncokb_evidence_by_api(query, parameters)
        elif len(re.findall(re.compile(r"([cA-Z0-9]+\b)-([cA-Z0-9]+\b) Fusion", re.IGNORECASE), alteration)) == 1:
            result = re.findall(re.compile(r"([cA-Z0-9]+\b)-([cA-Z0-9]+\b) Fusion", re.IGNORECASE), alteration)
            query = "structuralVariants"
            alias = {"Fusions": "FUSION", "Deletion": "DELETION"}
            parameters = {'hugoSymbolA': result[0][1], 'hugoSymbolB': result[0][0],
                          'structuralVariantType': 'FUSION', 'isFunctionalFusion': 'true'}
            evidence = get_oncokb_evidence_by_api(query, parameters)
        elif alteration in ["Deletion", "Amplification"]:  # "Overexpression"
            query = "copyNumberAlterations"
            alias = {"Amplification": "AMPLIFICATION", "Deletion": "DELETION"}
            parameters = {'hugoSymbol': gene, 'copyNameAlterationType': alias[alteration]}
            evidence = get_oncokb_evidence_by_api(query, parameters)
        elif any(key in alteration for key in ["Truncating Mutations", "in-frame deletions", "in-frame insertions",
                                               "missense mutations", "splice"]):
            query = "byProteinChange"
            alias = {"Truncating Mutations": "feature_truncation", "in-frame deletions": "inframe_deletion",
                     "in-frame insertions": "inframe_insertion", "missense mutations": "missense_variant",
                     "splice": "splice_region_variant"}
            variant_type = alias[next(key for key in alias.keys() if key in alteration)]
            parameters = {'hugoSymbol': gene, 'consequence': variant_type}
            evidence = get_oncokb_evidence_by_api(query, parameters)
        else:
            # not done
            # print(alteration)
            continue
        oncokb_evidence.append({"gene": gene, "variant": alteration, "evidence": evidence})

    with open("oncokb_evidence.json", 'w', encoding='utf-8') as f:
        json.dump(oncokb_evidence, f, sort_keys=True, indent=4,
                  separators=(', ', ': '), ensure_ascii=False)
















