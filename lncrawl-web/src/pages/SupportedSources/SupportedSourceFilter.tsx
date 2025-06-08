import {
  BookOutlined,
  LoginOutlined,
  SearchOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Button, Flex, Input, Select } from 'antd';
import React, { useEffect, useState } from 'react';

const defaultFilters = {
  search: '',
  language: undefined,
  features: [],
};

type Feature = 'has_manga' | 'has_mtl' | 'can_search' | 'can_login';

const featureOptions = [
  {
    value: 'has_manga',
    label: (
      <>
        <BookOutlined /> Manga
      </>
    ),
  },
  {
    value: 'has_mtl',
    label: (
      <>
        <TranslationOutlined /> MTL
      </>
    ),
  },
  {
    value: 'can_search',
    label: (
      <>
        <SearchOutlined /> Search
      </>
    ),
  },
  {
    value: 'can_login',
    label: (
      <>
        <LoginOutlined /> Login
      </>
    ),
  },
];

export type SourceFilterState = {
  search: string;
  language: string | undefined;
  features: Feature[];
};

export const SupportedSourceFilter: React.FC<{
  value?: SourceFilterState;
  onChange: (f: SourceFilterState) => void;
  languages: string[];
}> = ({ value = defaultFilters, onChange, languages }) => {
  const [filter, setFilter] = useState<SourceFilterState>(value);

  useEffect(() => {
    const tid = setTimeout(() => onChange(filter), 100);
    return () => clearTimeout(tid);
  }, [filter, onChange]);

  return (
    <Flex wrap align="center" gap={5}>
      <Input
        allowClear
        prefix={<SearchOutlined />}
        placeholder="Search by URL"
        value={filter.search}
        onChange={(e) => setFilter({ ...filter, search: e.target.value })}
        style={{ width: 220 }}
      />
      <Select
        allowClear
        placeholder="Language"
        value={filter.language}
        onChange={(val) => setFilter({ ...filter, language: val })}
        style={{ width: 110 }}
        options={languages.map((lang) => ({
          value: lang,
          label: (lang || 'ALL').toUpperCase(),
        }))}
      />
      <Select
        allowClear
        mode="multiple"
        placeholder="Features"
        style={{ minWidth: 150 }}
        value={filter.features}
        onChange={(features) => setFilter({ ...filter, features })}
        options={featureOptions}
      />
      <Button onClick={() => setFilter(defaultFilters)}>Clear</Button>
    </Flex>
  );
};
