import { DefinitionRendererBuilder, FormRendererBuilder, FormRendererConfig } from '../../renderers';
import { FormInput, ListInput, SectionContainer, SelectInput } from './components';
import { BooleanInput } from './components/BooleanInput';
import { FileInput } from './components/FileInput';
import { MultiFileInput } from './components/MultiFileInput';
import { MultiSelectInput } from './components/MultiSelectInput';

const chakraFormConfig: FormRendererConfig = {
  components: {
    Input: FormInput,
    Select: SelectInput,
    Switch: BooleanInput,
    MultiSelect: MultiSelectInput,
    File: FileInput,
    MultiFile: MultiFileInput,
    ListInput,
    SectionContainer,
  },
};

export const ChakraFormRenderer = FormRendererBuilder(chakraFormConfig);
export const CharaDefinitionRenderer = DefinitionRendererBuilder(chakraFormConfig.components);
