import type { SupportedSource } from '@/types';
import { FlagFilled, GlobalOutlined, StopOutlined } from '@ant-design/icons';
import { Avatar, Card, Flex, Tag, Typography } from 'antd';
import { useInView } from 'react-intersection-observer';
import { SourceFeatureIcons } from './SourceFeatureIcons';

export const SupportedSourceItem: React.FC<{
  source: SupportedSource;
  disabled?: boolean;
}> = ({ source, disabled }) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    rootMargin: '5px',
  });
  return (
    <Card
      ref={ref}
      size="small"
      hoverable={!disabled}
      style={{ opacity: disabled ? 0.8 : 1 }}
    >
      <Flex align="center" gap={15}>
        <Avatar
          style={{ backgroundColor: '#39f' }}
          src={inView ? `${source.url}/favicon.ico` : undefined}
          icon={disabled ? <StopOutlined /> : <GlobalOutlined />}
        />
        <Flex vertical style={{ flex: 1 }}>
          <Typography.Link
            strong
            delete={disabled}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {source.domain}
          </Typography.Link>
          {disabled && source.disable_reason && (
            <Typography.Text type="secondary">
              {source.disable_reason}
            </Typography.Text>
          )}
        </Flex>
        {source.language && (
          <Flex wrap align="center" gap="7px">
            <SourceFeatureIcons source={source} />
            <Tag icon={<FlagFilled />} style={{ margin: 0 }}>
              {source.language.toUpperCase()}
            </Tag>
          </Flex>
        )}
      </Flex>
    </Card>
  );
};
