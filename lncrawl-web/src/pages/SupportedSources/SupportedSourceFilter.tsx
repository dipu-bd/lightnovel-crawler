import {
  BookOutlined,
  LoginOutlined,
  SearchOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Button, Checkbox, Divider, Flex, Input, Select } from 'antd';
import React from 'react';

export type SourceFilterState = {
  search: string;
  language: string | undefined;
  has_manga: boolean;
  has_mtl: boolean;
  can_search: boolean;
  can_login: boolean;
  can_logout: boolean;
};

export const SupportedSourceFilter: React.FC<{
  filter: SourceFilterState;
  onChange: (f: SourceFilterState) => void;
  languages: string[];
}> = ({ filter, onChange, languages }) => {
  const handleChange = (key: keyof SourceFilterState, value: any) => {
    onChange({ ...filter, [key]: value });
  };

  const reset = () => {
    onChange({
      search: '',
      language: undefined,
      has_manga: false,
      has_mtl: false,
      can_search: false,
      can_login: false,
      can_logout: false,
    });
  };

  return (
    <Flex wrap align="center" gap={5}>
      <Input
        prefix={<SearchOutlined />}
        placeholder="Search by domain or URL"
        value={filter.search}
        onChange={(e) => handleChange('search', e.target.value)}
        allowClear
        style={{ width: 220 }}
      />
      <Select
        allowClear
        placeholder="Language"
        value={filter.language}
        onChange={(val) => handleChange('language', val)}
        style={{ width: 120 }}
        options={languages.map((lang) => ({
          value: lang,
          label: lang.toUpperCase(),
        }))}
      />
      <Divider type="vertical" size="small" />
      <Checkbox
        checked={filter.has_manga}
        onChange={(e) => handleChange('has_manga', e.target.checked)}
      >
        <BookOutlined /> Manga
      </Checkbox>
      <Checkbox
        checked={filter.has_mtl}
        onChange={(e) => handleChange('has_mtl', e.target.checked)}
      >
        <TranslationOutlined /> MTL
      </Checkbox>
      <Checkbox
        checked={filter.can_search}
        onChange={(e) => handleChange('can_search', e.target.checked)}
      >
        <SearchOutlined /> Search
      </Checkbox>
      <Checkbox
        checked={filter.can_login}
        onChange={(e) => handleChange('can_login', e.target.checked)}
      >
        <LoginOutlined /> Login
      </Checkbox>
      {/* <Checkbox
        checked={filter.can_logout}
        onChange={(e) => handleChange('can_logout', e.target.checked)}
      >
        <LogoutOutlined /> Logout
      </Checkbox> */}
      <Divider type="vertical" size="small" />
      <Button onClick={reset}>Reset</Button>
    </Flex>
  );
};
