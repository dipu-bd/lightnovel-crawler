import { Typography } from 'antd';
import './Marquee.css';
import type { TextProps } from 'antd/es/typography/Text';

const { Text } = Typography;

export const MarqueeText: React.FC<TextProps> = (props) => (
  <div className="marquee-container">
    <Text {...props} className={`${props.className} marquee-text`.trim()} />
  </div>
);
