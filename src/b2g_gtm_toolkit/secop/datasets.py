from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from b2g_gtm_toolkit.models.secop import SourcePlatform


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    dataset_id: str
    base_url: str
    source_platform: SourcePlatform
    field_map: Dict[str, str]
    default_filters: Dict[str, str] = field(default_factory=dict)
    record_url_template: Optional[str] = None

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/{self.dataset_id}.json"


SECOP_II_PROCESOS_FIELD_MAP: Dict[str, str] = {
    "id_del_proceso": "process_id",
    "nombre_entidad": "buyer_name",
    "entidad": "buyer_name",
    "nit_entidad": "buyer_nit",
    "departamento_entidad": "department",
    "ciudad_entidad": "municipality",
    "descripci_n_del_procedimiento": "object",
    "modalidad_de_contratacion": "modality",
    "estado_del_procedimiento": "status",
    "precio_base": "contract_value",
    "fecha_de_publicacion_del": "publication_date",
    "fecha_adjudicacion": "award_date",
    "fecha_de_recepcion_de": "deadline",
    "codigo_principal_de_categoria": "unspsc_primary",
    "urlproceso": "source_url",
    "proveedor_adjudicado": "supplier_name",
    "nombre_del_proveedor": "supplier_name",
    "documento_proveedor": "supplier_nit",
    "nit_del_proveedor_adjudicado": "supplier_nit",
}


SECOP_II_CONTRATOS_FIELD_MAP: Dict[str, str] = {
    "id_contrato": "contract_id",
    "proceso_de_compra": "process_id",
    "nombre_entidad": "buyer_name",
    "nit_entidad": "buyer_nit",
    "departamento": "department",
    "ciudad": "municipality",
    "objeto_del_contrato": "object",
    "modalidad_de_contratacion": "modality",
    "estado_contrato": "status",
    "valor_del_contrato": "contract_value",
    "fecha_de_firma": "publication_date",
    "fecha_de_inicio_del_contrato": "start_date",
    "fecha_de_fin_del_contrato": "end_date",
    "codigo_de_categoria_principal": "unspsc_primary",
    "urlproceso": "source_url",
    "proveedor_adjudicado": "supplier_name",
    "documento_proveedor": "supplier_nit",
}


SECOP_I_PROCESOS_FIELD_MAP: Dict[str, str] = {
    "uid": "process_id",
    "nombre_de_la_entidad": "buyer_name",
    "nit_de_la_entidad": "buyer_nit",
    "departamento_entidad": "department",
    "municipio_entidad": "municipality",
    "detalle_del_objeto_a_contratar": "object",
    "tipo_de_proceso": "modality",
    "estado_del_proceso": "status",
    "cuantia_proceso": "contract_value",
    "fecha_de_cargue_en_el_secop": "publication_date",
    "fecha_de_firma_del_contrato": "award_date",
    "id_familia": "unspsc_primary",
    "ruta_proceso_en_secop_i": "source_url",
    "nom_raz_social_contratista": "supplier_name",
    "identificacion_del_contratista": "supplier_nit",
}


DATASETS: Dict[str, DatasetSpec] = {
    "secop_ii_procesos": DatasetSpec(
        name="secop_ii_procesos",
        dataset_id="p6dx-8zbt",
        base_url="https://www.datos.gov.co/resource",
        source_platform=SourcePlatform.SECOP_II,
        field_map=SECOP_II_PROCESOS_FIELD_MAP,
        default_filters={},
    ),
    "secop_ii_contratos": DatasetSpec(
        name="secop_ii_contratos",
        dataset_id="jbjy-vk9h",
        base_url="https://www.datos.gov.co/resource",
        source_platform=SourcePlatform.SECOP_II,
        field_map=SECOP_II_CONTRATOS_FIELD_MAP,
        default_filters={},
    ),
    "secop_i_procesos": DatasetSpec(
        name="secop_i_procesos",
        dataset_id="f789-7hwg",
        base_url="https://www.datos.gov.co/resource",
        source_platform=SourcePlatform.SECOP_I,
        field_map=SECOP_I_PROCESOS_FIELD_MAP,
        default_filters={},
    ),
}


def get_dataset(name: str) -> DatasetSpec:
    if name not in DATASETS:
        raise KeyError(f"Dataset SECOP no registrado: {name}")
    return DATASETS[name]


def list_dataset_names() -> list[str]:
    return list(DATASETS.keys())
