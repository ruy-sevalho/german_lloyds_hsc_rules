from dataclass_tools.tools import DeSerializerOptions, PrintMetadata

abv_registry: list[DeSerializerOptions] = []
ABREVIATION_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Name", abreviation="Abrevtion/Symbol")
)
