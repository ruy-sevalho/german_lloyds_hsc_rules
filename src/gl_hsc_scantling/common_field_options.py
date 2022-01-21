from dataclass_tools.tools import DeSerializerOptions

NAMED_FIELD_OPTIONS = DeSerializerOptions(subs_by_attr="name")
LAMINATE_OPTIONS = DeSerializerOptions(
    subs_by_attr="name", subs_collection_name="laminates"
)