import React from 'react';
import Box from "@mui/material/Box";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import HelpIcon from '@mui/icons-material/Help';

import {HtmlTooltip} from "src/sections/dashboard/applications/HtmlTooltip";

type Props = {
  id: string;
  label: string
  helpTitle: string
  helpLong?: React.ReactNode
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => void
  checked: boolean
}
export const GrantTypeField = ({ id, checked, label, helpTitle, helpLong, onChange}: Props): React.ReactElement => {
  return (
    <Box>
      <FormControlLabel control={<Checkbox id={id} checked={checked} onChange={onChange}/>} label={label}/>
      <HtmlTooltip
        title={
          <React.Fragment>
            <Typography color="inherit">{helpTitle}</Typography>
            {helpLong}
          </React.Fragment>
        }
      >
        <IconButton size={"small"}><HelpIcon color={'primary'} fontSize={"small"}/></IconButton>
      </HtmlTooltip>
    </Box>
  );
};
