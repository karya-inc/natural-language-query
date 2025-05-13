import { ListInputProps, MultiFileInputProps } from '../types/InputComponentProps';
import {
  flattenData,
  joiSchema,
  ParameterArray,
  parameterArrayFromGroups,
  ParameterForm,
  unflattenData,
} from 'src/helpers/parameter-spec/src/Index';
import Joi from 'joi';
import { ChangeEventHandler, FormEventHandler, useCallback, useEffect, useMemo, useState } from 'react';
import _ from 'lodash';
import { FormInputRenderer } from '../types/CustomRenderer';

export type FormChangedHook<T> = (id: keyof T, control: UseFormReturn<T>) => void;

export type RendererInfo<Props> = {
  type: string;
  component: FormInputRenderer<Props>;
  props: Props;
};

export type UseFormConfig<T> = {
  onSubmit?: (data: T) => void;
  formChangedHook?: FormChangedHook<T>;
  parameters: ParameterForm<T>;
  initialState?: Partial<T>;
  isKeyPath?: boolean;
  hideDisabledFields?: boolean;
  isEmptyStringValid?: boolean;
  sectionless?: boolean;
  renderers?: RendererInfo<any>[];
};

export type FormContext<T> = {
  parameters: ParameterForm<T>;
  form: Partial<T>;
  errors: Partial<T>;
  handleChange: ChangeEventHandler<HTMLInputElement | HTMLSelectElement>;
  handleBooleanChange: ChangeEventHandler<HTMLInputElement>;
  handleFileChange: ChangeEventHandler<HTMLInputElement>;
  handleMultiFileChange: MultiFileInputProps['onChange'];
  handleJsonChange: ChangeEventHandler<HTMLInputElement>;
  handleListChange: ListInputProps['onChange'];
  setFormField: <Key extends keyof T>(id: Key, value: any) => void;
  renderers?: RendererInfo<any>[];
  sectionless?: boolean;
  hideDisabledFields?: boolean;
};
export type UseFormReturn<T> = {
  ctx: FormContext<T>;
  validate: () => Joi.ValidationResult<T>;
  handleSubmit: FormEventHandler<HTMLFormElement>;
  setFormField: (id: keyof T, value: any) => void;
  setError: (id: keyof T, err: string) => void;
  resetForm: () => void;
  get: <Key extends keyof T>(id: Key, fallback?: T[Key]) => Partial<T>[Key];
  setForm: (newForm: Partial<T>) => void;
  setFormRaw: React.Dispatch<React.SetStateAction<Partial<T>>>;
  setParameterForm: React.Dispatch<React.SetStateAction<ParameterForm<T>>>;
};

export function useForm<T = { [id: string]: any }>(config: UseFormConfig<T>): UseFormReturn<T> {
  const { isKeyPath, onSubmit, formChangedHook } = config;

  const [parameterForm, setParameterForm] = useState<ParameterForm<T>>(config.parameters);
  const [allParameters, setAllParameters] = useState<ParameterArray<T>>([]);
  const [form, setFormRaw] = useState<Partial<T>>(config.initialState ?? {});
  const [errors, setErrors] = useState<Partial<T>>({});
  const [changedFieldId, setChangedFieldId] = useState<keyof T | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const schema = useMemo(() => joiSchema<T>(allParameters, { isKeyPath }), [allParameters]);

  useEffect(() => {
    const parameterArray = parameterArrayFromGroups(parameterForm);
    setAllParameters(parameterArray);

    let isFormUpdated = false;

    if (!isDirty) {
      if (config.initialState) {
        if (isKeyPath) {
          // @ts-expect-error - This is a hack to get around the type error
          setFormRaw(flattenData(parameterArray, config.initialState));
        } else {
          setFormRaw(config.initialState);
        }
        isFormUpdated = true;
      } else {
        parameterArray.forEach((param) => {
          if ('initial' in param && param.initial !== undefined) {
            setFormField(param.id, param.initial);
            isFormUpdated = true;
          }
        });
      }
    }

    if (isFormUpdated) {
      setIsDirty(true);
    }
  }, [parameterForm]);

  useEffect(() => {
    setParameterForm(config.parameters);
  }, [config.parameters]);

  const validate = useCallback(() => {
    let preValidationForm = form;

    if (!config.isEmptyStringValid) {
      const prevalidationFormEntries = Object.entries(form).filter(([_, value]) => value !== '');
      preValidationForm = Object.fromEntries(prevalidationFormEntries) as Partial<T>;
    }

    // Unflatten the form if the ids represent a path
    if (isKeyPath) {
      preValidationForm = unflattenData<T>(allParameters, preValidationForm);
    }

    const result = schema.validate(preValidationForm, {
      stripUnknown: true,
    });

    const { error } = result;

    // If error, set form errors
    if (error) {
      const updatedErrors: Partial<T> = {};
      error.details.forEach((currError) => {
        const id = currError.path.join('.');
        // @ts-ignore
        updatedErrors[id] = currError.message.replaceAll('"', '');
      });

      setErrors(updatedErrors);
    }

    // Return the validation result
    return result;
  }, [schema, form, isKeyPath]);

  const handleSubmit: FormEventHandler<HTMLFormElement> = useCallback(
    async (e) => {
      e.preventDefault();
      const { value, error } = validate();
      if (error) {
        return;
      }
      setErrors({});
      if (onSubmit) {
        onSubmit(value);
      }
    },
    [validate, onSubmit],
  );

  const setError = useCallback((id: keyof T, err: string) => {
    setErrors((errors) => ({ ...errors, [id]: err }));
  }, []);

  const setForm = useCallback(
    (newForm: Partial<T>) => {
      if (isKeyPath) {
        // @ts-expect-error - This is a hack to get around the type error
        setFormRaw(flattenData(allParameters, newForm));
      } else {
        setFormRaw(newForm);
      }
    },
    [formChangedHook, allParameters],
  );

  useEffect(() => {
    if (isKeyPath) {
      const flattenedForm = flattenData(allParameters, form);
      // HACK: Prevent infinite rerenders when the parameters are updated based on the form values
      if (!_.isEqual(flattenedForm, form)) {
        // @ts-expect-error - This is a hack to get around the type error
        setFormRaw(flattenedForm);
      }
    }
  }, [allParameters, isKeyPath]);

  const setFormField = useCallback(
    <Key extends keyof T>(id: Key, value: any) => {
      setFormRaw((form) => ({ ...form, [id]: value }));
      setChangedFieldId(id);
      setIsDirty(true);
    },
    [formChangedHook],
  );

  const handleChange: ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> = useCallback(
    (e) => {
      const id = e.target.id as keyof T;
      const value = e.target.value;
      setFormField(id, value);
    },
    [],
  );

  const handleFileChange: ChangeEventHandler<HTMLInputElement> = useCallback((e) => {
    const target_id = e.target.id as keyof T;
    if (e.target.files) {
      const file = e.target.files[0];
      if (file) {
        setFormField(target_id, file);
      }
    } else {
      setFormRaw((form) => {
        delete form[target_id];
        return form;
      });
    }
  }, []);

  const handleMultiFileChange: MultiFileInputProps['onChange'] = useCallback((id, files) => {
    setFormField(id as keyof T, files);
  }, []);

  const handleBooleanChange: ChangeEventHandler<HTMLInputElement> = useCallback((e) => {
    setFormField(e.target.id as keyof T, e.target.checked);
  }, []);

  const handleListChange: ListInputProps['onChange'] = useCallback((id, values) => {
    setFormField(id as keyof T, values);
  }, []);

  const handleJsonChange: ChangeEventHandler<HTMLInputElement> = useCallback((e) => {
    const target_id = e.target.id as keyof T;
    if (e.target.files) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.readAsText(file);
      reader.addEventListener(
        'load',
        () => {
          const resultJson = JSON.parse(reader.result as string);
          setFormField(target_id, resultJson);
        },
        false,
      );
    } else {
      setFormField(target_id, undefined);
    }
  }, []);

  const resetForm = () => {
    setFormRaw({});
    setErrors({});
  };

  const get = <Key extends keyof T>(id: Key, fallback?: T[Key]) => {
    return form[id] ?? fallback;
  };

  const ctx: UseFormReturn<T>['ctx'] = {
    form,
    errors,
    handleChange,
    handleFileChange,
    handleMultiFileChange,
    handleJsonChange,
    handleBooleanChange,
    handleListChange,
    setFormField,
    parameters: parameterForm,
    renderers: config.renderers ?? [],
    sectionless: config.sectionless,
    hideDisabledFields: config.hideDisabledFields,
  };

  const formControl = {
    ctx,
    validate,
    handleSubmit,
    resetForm,
    setFormField,
    setError,
    get,
    setForm,
    setFormRaw,
    setParameterForm,
  };

  useEffect(() => {
    if (changedFieldId && formChangedHook) {
      formChangedHook(changedFieldId, formControl);
      setChangedFieldId(null);
    }
  }, [changedFieldId]);

  return formControl;
}
