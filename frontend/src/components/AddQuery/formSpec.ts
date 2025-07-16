import { ParameterArray, ParameterForm } from "src/helpers/parameter-spec/src/Index";

export type QueryForm = {
  id: string;
  name: string;
  initial: any;
  list: [any];
  [key: string]: any;
};

export type StoredDynamicParam = {
  _internalId: string;
  id: string;
  label: string;
  type: string;
  initial: any;
  list?: {};
};

export const buildQueryForm = (): ParameterForm<QueryForm> => [{
  label: "",
  required: false,
  parameters: [
    {
      id: "query",
      label: "Query",
      required: true,
      placeholder: "SQL Query",
      type: "string",
      initial: "",
      extraProps: { width: "700px" },
      long: true,
    },{
      id: "query_name",
      label: "Query Name",
      required: true,
      placeholder: "Name",
      type: "string",
      initial: "",
    },{
      id: "query_description",
      label: "Query Description",
      placeholder: "A short description for the query",
      required: true,
      type: "string",
      initial: "",
      long: true,
    },{
      id: "query_id",
      label: "Query Id (Optional)",
      placeholder: "Query Id",
      required: false,
      type: "string",
      extraProps: { width: "400px" },
      initial: "",
    },{
      id: "query_type",
      label: "Query Type",
      required: false,
      type: "enum",
      list: { static: "static", dynamic: "dynamic" },
      initial: "static",
    },{
      id: "user_emails",
      label: "User Emails to share with (comma-separated)",
      required: false,
      type: "list",
      initial: [],
      extraProps: { width: "250px" },
      delimiters: [","],
    }
  ]
}];

export const buildDynamicParamForm = (
  typeSpecificParams: ParameterArray<QueryForm>
): ParameterForm<QueryForm> => [{
  label: "",
  required: false,
  parameters: [
    {
      id: "id",
      label: "Parameter Id",
      required: true,
      placeholder: "Id should be the same as in the query",
      type: "string",
      extraProps: { width: "300px" },
    },{
      id: "label",
      label: "Parameter Label",
      required: true,
      placeholder: "Parameter Label",
      type: "string",
      extraProps: { width: "300px" },
    },{
      id: "type",
      label: "Parameter Type",
      required: true,
      type: "enum",
      initial: "int",
      list: {
        "int": "int",
        "float": "float",
        "string": "string",
        "list": "list",
        "boolean": "boolean",
        "enum": "enum",
        "enum_multi": "enum_multi",
        "date": "date",
        "time": "time",
        "datetime-local": "datetime-local",
      },
    },
    ...typeSpecificParams
  ]
}];

export const getTypeSpecificParams = (
  selectedType: string
): ParameterArray<QueryForm> => {
  switch (selectedType) {
    case 'int':
    case 'float':
    case 'string':
    case 'date':
    case 'time':
    case 'datetime-local':
      return [
        {
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: selectedType,
        }
      ] as ParameterArray<QueryForm>;
    case 'enum':
      return [
        {
          id: `list_${selectedType}`,
          label: "Enum Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        },{
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: "string",
        }
      ];
    case 'enum_multi':
      return [
        {
          id: `list_${selectedType}`,
          label: "Enum Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        },{
          id: `initial_${selectedType}`,
          label: "Initial Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        }
      ];
    case 'boolean':
      return [{
        id: `initial_${selectedType}`,
        label: "Initial Value",
        required: true,
        type: "enum",
        list: { "true": "true", "false": "false" },
      }];
    case 'list':
      return [{
        id: `initial_${selectedType}`,
        label: "Initial List Values (comma-separated)",
        required: true,
        type: "list",
        delimiters: [","],
      }];
    default:
      return [];
  }
};
