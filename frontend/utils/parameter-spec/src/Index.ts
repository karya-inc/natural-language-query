// Copyright (c) DAIA Tech Pvt Ltd.
//
// Module to help with parameter specification.

import Joi from 'joi';
import _ from 'lodash';

export type ParameterType =
  | { type: 'string'; long?: boolean; placeholder?: string }
  | { type: 'int'; min?: number; max?: number }
  | { type: 'float'; min?: number; max?: number }
  | { type: 'boolean'; required: false; valid?: undefined }
  | { type: 'enum'; list: { [id: string]: string }; valid?: undefined }
  | { type: 'enum_multi'; list: { [id: string]: string }; valid?: undefined }
  | { type: 'list'; delimiters?: string[]; valid?: undefined }
  | { type: 'time' }
  | { type: 'date' }
  | { type: 'json_object'; valid?: undefined }
  | {
      type: 'json_array';
      itemType?: ParameterType['type'];
      valid?: undefined;
      /**
       * Parameter Definitions for items within the array
       * This is used to flatten the array such that the each item has the id of the form `paramId.itemId`
       * Unflatenning the array will reconstruct the array
       */
      items?: ParameterArray;
    }
  | { type: 'json'; valid?: undefined }
  | { type: 'multi_file'; showFileNames?: boolean }
  | {
      type: 'fixed';
      value: string | number | boolean | object;
      required: false;
    }
  | { type: 'file'; acceptedTypes?: string }; //json

/**
 * Specify Parameter Defaults
 *
 * default: Specifies the value to be used if validation fails due to missing value
 * initial: Specifies the initial value of the field (set before validation by the renderer)
 */
type DefaultValue<T> =
  | {
      default?: T;
      required: false;
    }
  | {
      initial?: T;
    };

type RequirementType = 'EQUALS' | 'NOT_EQUALS';
type RequirementDefinition<T> =
  | [Extract<keyof T, string>, T[keyof T]]
  | [Extract<keyof T, string>, T[keyof T], RequirementType]
  | [Extract<keyof T, string>, T[keyof T][], 'IN' | 'NOT_IN'];

/**
 * Specify dependencies for parameter
 * TODO: Figure out joi implementation
 *
 * requires - array of tuples of format [key, val] used to specify parameter dependencies.
 *
 * requiredIfSatisfied - mark the field as required if the dependencies specified in requires
 * are satisfied
 */
type ParameterDependecy<T> =
  | {
      requires: RequirementDefinition<T>[];
      requiredIfSatisfied: boolean;
    }
  | {};

/**
 * Parameter specification
 *
 * id: Identifier for the parameter. Should be unique within an array of parameters.
 * type: Type of the parameter. Used to define the Joi Schema type
 * label: Label for the parameter. Used as label in React text input
 * description: Full description of the parameter. Used as part of React text input
 * required: Indicated if the parameter is required or optional
 * valid: Specifies the set valid values for the parameter. Other values are rejected.
 * renderer: Allows usage of custom components for rendering a component
 */
export type ParameterDefinition<T extends keyof V, V = any> = {
  id: Extract<T, string>;
  label: string;
  description?: string;
  required: boolean;
  valid?: V[T][];
  renderer?: string;
  extraProps?: Record<string, any>;
} & ParameterDependecy<V> &
  DefaultValue<V[T]> &
  ParameterType;

/**
 * A group of parameters related parameters (typically renderer together)
 *
 * label: Label for the parameter group. Used as the label for a group of parameters
 * description: Full description of the parameter group.
 * required: Indicated if the parameter group is required or optional
 */
export type ParameterSection<T> = {
  label: string;
  description?: string;
  parameters: ParameterArray<T>;
  required: boolean;
};

/**
 * Array of parameter definitions
 */
export type ParameterArray<T = { [id: string]: any }> = ParameterDefinition<keyof T, T>[];

/**
 * Array of parameter groups
 */
export type ParameterForm<T = { [id: string]: any }> = ParameterSection<T>[];

/**
 * Extract all parameters in the form of parameter array from parameter form
 * Useful for validating  parameter form
 * @param groups List of parameter groups
 */
export function parameterArrayFromGroups<ParamType>(groups: ParameterForm<ParamType>) {
  return groups.reduce<ParameterArray<ParamType>>((params, group) => [...params, ...group.parameters], []);
}

export function flattenData<T extends object>(params: ParameterArray<T>, data: T): Record<string, any> {
  const clonedData = _.cloneDeep(data);
  let flatData: any = {};
  // Iterate through each parameter and set the required values in flatData
  // Return the each of the keys used in the process
  const keysUsed = params.map((param) => {
    const { id } = param;
    const value = _.get(clonedData, id);

    if (param.type === 'json_array' && param.items) {
      // For each item in the array, set the corresponding value in the flatData
      param.items.forEach((item, index) => {
        const itemId = `${id}.${item.id}`;
        const itemPath = `${id}.${index}`;
        flatData[itemId] = _.get(clonedData, itemPath);
      });
    }

    if (value !== undefined) {
      flatData[id] = value;
    }

    return id;
  });

  // Remove the properties used from the cloned data
  keysUsed.forEach((key) => {
    _.unset(clonedData, key);
  });

  // Add the remaining (potentially unflattenData) data to the flatData
  flatData = { ...flatData, ...clonedData };

  return flatData;
}

export function unflattenData<T>(params: ParameterArray<T>, flatData: Record<string, any>): T {
  const data: any = {};
  params.forEach((param) => {
    const { id } = param;
    let value = flatData[id];
    if (param.type === 'json_array' && param.items) {
      // Reconstruct the array
      value = param.items.map((item) => _.get(flatData, `${id}.${item.id}`));
    }
    if (value !== undefined) {
      _.set(data, id, value);
    }
  });

  return data as T;
}

type SchemaType = 'OBJECT' | 'ARRAY';
type SchemaGeneartionOptions<IsKeyPath extends boolean, ResultType extends SchemaType> = {
  isKeyPath?: IsKeyPath;
  schemaOverlapResolution?: 'OVERWRITE' | 'CONCAT' | 'ALTERNATE';
  schemaType?: ResultType;
};
type GeneratedSchema<ParamsType, ResultType extends SchemaType> = ResultType extends 'OBJECT'
  ? Joi.ObjectSchema<ParamsType>
  : Joi.ArraySchema<ParamsType[]>;

/**
 * Converts a parameter array to a Joi schema that can be used to
 * validate an object of that type.
 * @param params List of parameters
 */
export function joiSchema<ParamsType, IsKeyPath extends boolean = boolean, ResultType extends SchemaType = 'OBJECT'>(
  params: ParameterArray<ParamsType>,
  options: SchemaGeneartionOptions<IsKeyPath, ResultType> = {},
): GeneratedSchema<ParamsType, ResultType> {
  const schemaMap: Joi.SchemaMap<ParamsType> = {};
  params.forEach((param) => {
    const { id, label, description, required } = param;
    let base:
      | Joi.StringSchema
      | Joi.BooleanSchema
      | Joi.NumberSchema
      | Joi.ArraySchema
      | Joi.ObjectSchema
      | Joi.ArraySchema
      | Joi.AnySchema;
    switch (param.type) {
      case 'string':
        base = Joi.string().empty('');
        break;
      case 'boolean':
        base = Joi.boolean().default(false);
        break;
      case 'int':
        base = Joi.number()
          .integer()
          .min(param.min ?? Number.MIN_SAFE_INTEGER)
          .max(param.max ?? Number.MAX_SAFE_INTEGER);
        break;
      case 'float':
        base = Joi.number()
          .min(param.min ?? Number.MIN_SAFE_INTEGER)
          .max(param.max ?? Number.MAX_SAFE_INTEGER);
        break;
      case 'enum': {
        const values = Object.keys(param.list);
        base = Joi.string()
          .valid(...values)
          .empty('');
        break;
      }
      case 'enum_multi': {
        const values = Object.keys(param.list);
        base = Joi.array().items(
          Joi.string()
            .valid(...values)
            .empty(''),
        );
        break;
      }
      case 'list':
        base = Joi.array().items(Joi.string());
        break;
      case 'time':
        base = Joi.string()
          .regex(/^([01]\d|2[0-3]):?([0-5]\d)$/)
          .empty('');
        break;
      case 'date':
        base = Joi.string()
          .regex(/^\d\d\d\d-\d\d-\d\d$/)
          .empty('');
        break;
      case 'file':
        base = Joi.any();
        break;
      case 'json_object':
        base = Joi.object();
        break;
      case 'json_array':
        if (param.items) {
          base = joiSchema(param.items, {
            isKeyPath: options.isKeyPath,
            schemaType: 'ARRAY',
          });
        } else {
          base = Joi.array().items(Joi.any());
        }
        break;
      case 'json':
        base = Joi.alternatives(Joi.object(), Joi.array().items(Joi.any()));
        break;
      case 'multi_file':
        base = Joi.array().items(Joi.any());
        break;
      case 'fixed':
        base = Joi.any().default(param.value);
        break;
    }
    base = base.label(label);
    if (description) {
      base.description(description);
    }

    if ('default' in param && param.default) {
      base = base.default(param.default);
    }

    if (param.valid) {
      base = base.valid(...param.valid);
    }

    if (required) {
      base = base.required();
    }

    if ('requires' in param && param.requires) {
      // Build the schema for marking the field as required or optional
      const requiredIfSatisfied = 'requiredIfSatisfied' in param && param.requiredIfSatisfied;
      if (requiredIfSatisfied) {
        base = base.required();
      }

      for (const requirement of param.requires) {
        const [key, value, type = 'EQUALS'] = requirement;
        let requirementSchema: Joi.Schema = Joi.any();
        let isUndefinedExpected = false;
        switch (type) {
          case 'EQUALS':
            if (value === undefined) {
              isUndefinedExpected = true;
              break;
            }
            if (value instanceof Array) {
              throw new Error('Array values are not supported for EQUALS requirement. Try using IN or NOT_IN');
            }

            requirementSchema = Joi.valid(value);
            break;
          case 'NOT_EQUALS':
            if (value === undefined) {
              isUndefinedExpected = true;
              break;
            }
            if (value instanceof Array) {
              throw new Error('Array values are not supported for EQUALS requirement. Try using IN or NOT_IN');
            }

            requirementSchema = Joi.invalid(value);
            break;
          case 'IN':
          case 'NOT_IN':
            if (!(value instanceof Array)) {
              throw new Error('IN requirement expects an array of values');
            }

            // Handle undefined values in the array
            const definedValues = value.filter((v) => {
              if (v !== undefined) {
                return true;
              }
              isUndefinedExpected = true;
              return false;
            });

            // Apply the requirement based on the type (IN or NOT_IN)
            if (type === 'IN') {
              requirementSchema = Joi.valid(...(definedValues as any[]));
            } else {
              requirementSchema = Joi.invalid(...(definedValues as any[]));
            }

            break;
          default:
            throw new Error(`Unsupported requirement type: ${type}`);
        }

        if (!isUndefinedExpected) {
          // Mark the condition field as required
          // Don't mark the field as required if the expected value is undefined
          // NOTE: This ensures the condition fails when the key is not present in the object.
          requirementSchema = requirementSchema.required();
        }

        base = Joi.when(`/${key}`, {
          is: requirementSchema,
          then: base,
          otherwise: Joi.optional().strip(),
        });
      }
    }

    if (options.isKeyPath) {
      const existingSchema = _.get(schemaMap, id) as Joi.AnySchema;
      if (existingSchema) {
        const stratergy = options.schemaOverlapResolution ?? 'OVERWRITE';
        switch (stratergy) {
          case 'OVERWRITE':
            // Ignore the existing schema and overwrite it
            break;
          case 'CONCAT':
            base = base.concat(existingSchema);
            break;

          case 'ALTERNATE':
            base = Joi.alternatives(existingSchema, base);
            break;
        }
      }

      _.set(schemaMap, id, base);
    } else {
      schemaMap[id] = base;
    }
  });

  if (options.schemaType && options.schemaType === 'ARRAY') {
    const values: Joi.Schema[] = Object.values(schemaMap);
    // @ts-expect-error
    return Joi.array().ordered(...values) as GeneratedSchema<ParamsType, 'ARRAY'>;
  }
  // @ts-expect-error
  return Joi.object(schemaMap) as GeneratedSchema<ParamsType, 'OBJECT'>;
}
