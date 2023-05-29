import type {FC} from 'react';
import React, {useCallback, useEffect, useState} from 'react';
import toast from 'react-hot-toast';
import * as Yup from 'yup';
import {useFormik} from 'formik';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import FormGroup from '@mui/material/FormGroup';
import FormHelperText from '@mui/material/FormHelperText';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import Grid from '@mui/material/Unstable_Grid2';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import type {File} from 'src/components/file-dropzone';
import {FileDropzone} from 'src/components/file-dropzone';
import {useRouter} from 'src/hooks/use-router';
import {paths} from 'src/paths';
import {Application} from "src/types/application";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";
import {GrantTypeField} from "src/sections/dashboard/applications/GrantTypeField";
import {applicationsApi} from "src/service/applications/ApplicationApiService";

interface CategoryOption {
  label: string;
  value: string;
}

const categoryOptions: CategoryOption[] = [
  {
    label: 'Healthcare',
    value: 'healthcare'
  },
  {
    label: 'Makeup',
    value: 'makeup'
  },
  {
    label: 'Dress',
    value: 'dress'
  },
  {
    label: 'Skincare',
    value: 'skincare'
  },
  {
    label: 'Jewelry',
    value: 'jewelry'
  },
  {
    label: 'Blouse',
    value: 'blouse'
  }
];

type Values = {
  client_id?: string;
  client_name: string;
  client_secret?: string;
  description?: string;
  tenant: string;
  authorization_code_grant: boolean;
  client_credentials_grant: boolean;
  implicit_grant: boolean;
  password_grant: boolean;
  refresh_token_grant: boolean;
  device_code_grant: boolean;

  submit?: boolean;
}

const emptyValues: Values = {
  client_name: '',
  tenant: 'master',
  authorization_code_grant: true,
  client_credentials_grant: false,
  implicit_grant: false,
  password_grant: false,
  refresh_token_grant: true,
  device_code_grant: true,
};

const validationSchema = Yup.object({
  client_secret: Yup.string().max(255),
  description: Yup.string().max(5000),
  authorization_code_grant: Yup.boolean().required(),
  client_credentials_grant: Yup.boolean().required(),
  implicit_grant: Yup.boolean().required(),
  password_grant: Yup.boolean().required(),
  refresh_token_grant: Yup.boolean().required(),
  device_code_grant: Yup.boolean().required(),
});

type Props = {
  application?: Application
}

export const ApplicationDetailsTab: FC<Props> = ({application}) => {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const formik = useFormik({
    initialValues: application ?? emptyValues,
    enableReinitialize: true,
    validationSchema,
    onSubmit: async (values, helpers): Promise<void> => {
      try {
        if (application) {
          applicationsApi.updateApplication({ application: values });
        } else {
        }
        // NOTE: Make API request
        toast.success('Application created');
        router.push(paths.dashboard.applications.index);
      } catch (err) {
        console.error(err);
        toast.error('Something went wrong!');
        helpers.setStatus({success: false});
        helpers.setErrors({submit: err.message});
        helpers.setSubmitting(false);
      }
    }
  });
  let saveLabelText = 'Create';
  if (application) {
    saveLabelText = 'Update';
  }
  const handleFilesDrop = useCallback(
    (newFiles: File[]): void => {
      setFiles((prevFiles) => {
        return [...prevFiles, ...newFiles];
      });
    },
    []
  );

  const handleFileRemove = useCallback(
    (file: File): void => {
      setFiles((prevFiles) => {
        return prevFiles.filter((_file) => _file.path !== file.path);
      });
    },
    []
  );

  const handleFilesRemoveAll = useCallback(
    (): void => {
      setFiles([]);
    },
    []
  );

  return (
    <form
      onSubmit={formik.handleSubmit}
    >
      <Stack spacing={4}>
        <Card>
          <CardContent>
            <Grid
              container
              spacing={3}
            >
              <Grid
                xs={12}
                md={4}
              >
                <Typography variant="h6">
                  Basic details
                </Typography>
              </Grid>
              <Grid
                xs={12}
                md={8}
              >
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    id="client_name"
                    name="client_name"
                    label="Application Name"
                    value={formik.values.client_name}
                    onBlur={formik.handleBlur}
                    onChange={formik.handleChange}
                    error={formik.touched.client_name && !!formik.errors.client_name}
                    helperText={formik.touched.client_name && formik.errors.client_name}
                  />
                  <TextField
                    fullWidth
                    id="domain_name"
                    name="domain_name"
                    label="Domain Name"
                    value={'master.i-1.app'}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton size="small" sx={{p: 0}} color={"primary"}>
                            <ContentCopyIcon fontSize={'small'}/>
                          </IconButton>
                        </InputAdornment>
                      )
                    }}
                    disabled
                  />

                  <TextField
                    error={!!(formik.touched.client_id && formik.errors.client_id)}
                    fullWidth
                    helperText={formik.touched.client_id && formik.errors.client_id}
                    label="Client ID"
                    id="client_id"
                    name="client_id"
                    onBlur={formik.handleBlur}
                    onChange={formik.handleChange}
                    value={formik.values.client_id}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton size="small" sx={{p: 0}} color={"primary"}>
                            <ContentCopyIcon fontSize={'small'}/>
                          </IconButton>
                        </InputAdornment>
                      ),
                      style: {fontFamily: "monospace"},
                    }}
                    disabled
                  />

                  <TextField
                    error={!!(formik.touched.client_secret && formik.errors.client_secret)}
                    fullWidth
                    helperText={formik.touched.client_secret && formik.errors.client_secret}
                    label="Client Secret"
                    name="client_secret"
                    onBlur={formik.handleBlur}
                    onChange={formik.handleChange}
                    value={formik.values.client_secret}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton size="small" sx={{p: 0}} color={"primary"}>
                            <ContentCopyIcon fontSize={'small'}/>
                          </IconButton>
                        </InputAdornment>
                      ),
                      style: {fontFamily: "monospace"},
                    }}
                    type={"password"}
                    disabled
                  />

                  <div>
                    <Typography
                      color="text.secondary"
                      sx={{mb: 2}}
                      variant="subtitle2"
                    >
                      Description
                    </Typography>
                    <TextField
                      error={!!(formik.touched.description && formik.errors.description)}
                      multiline
                      rows={4}
                      fullWidth
                      helperText={formik.touched.description && formik.errors.description}
                      label="Write something"
                      name="description"
                      onBlur={formik.handleBlur}
                      onChange={formik.handleChange}
                      value={formik.values.description}
                    />
                    {!!(formik.touched.description && formik.errors.description) && (
                      <Box sx={{mt: 2}}>
                        <FormHelperText error>
                          {formik.errors.description}
                        </FormHelperText>
                      </Box>
                    )}
                  </div>
                </Stack>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Grid
              container
              spacing={3}
            >
              <Grid
                xs={12}
                md={4}
              >
                <Stack spacing={1}>
                  <Typography variant="h6">
                    Images
                  </Typography>
                  <Typography
                    color="text.secondary"
                    variant="body2"
                  >
                    Images will appear in the store front of your website.
                  </Typography>
                </Stack>
              </Grid>
              <Grid
                xs={12}
                md={8}
              >
                <FileDropzone
                  accept={{'image/*': []}}
                  caption="(SVG, JPG, PNG, or gif maximum 900x400)"
                  files={files}
                  onDrop={handleFilesDrop}
                  onRemove={handleFileRemove}
                  onRemoveAll={handleFilesRemoveAll}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Grid
              container
              spacing={3}
            >
              <Grid
                xs={12}
                md={4}
              >
                <Typography variant="h6">
                  OAuth
                </Typography>
              </Grid>
              <Grid
                xs={12}
                md={8}
              >
                <Stack spacing={3}>
                  <div>
                    <Typography
                      color="text.secondary"
                      sx={{mb: 2}}
                      variant="subtitle2"
                    >
                      Grant Type
                    </Typography>
                    <FormGroup sx={{paddingLeft: 4}}>
                      <GrantTypeField checked={formik.values.authorization_code_grant}
                                      id={"authorization_code_grant"}
                                      onChange={formik.handleChange}
                                      label={"Authorization Code"} helpTitle={"Authorization Code grant"}
                                      helpLong={
                                        <>
                                          This is the most common grant type. Your application asks for permission from
                                          the user
                                          and then exchanges a code for an access token.
                                          <br/>
                                          For more information, see <a
                                          href={'https://oauth.net/2/grant-types/authorization-code/'}>OAuth 2.0
                                          Authorization Code Grant</a>.
                                        </>}
                      />
                      <GrantTypeField checked={formik.values.client_credentials_grant}
                                      onChange={formik.handleChange}
                                      id={"client_credentials_grant"}
                                      label={"Client Credentials"} helpTitle={"Client Credentials grant"}
                                      helpLong={
                                        <>
                                          The Client Credentials grant type is used by clients to obtain an access token
                                          outside of the context of a user.
                                          This is typically used by backend services and CLI scripts to access resources
                                          about themselves rather than to access
                                          a user&apos;s resources.
                                          <br/>
                                          For more information, see <a
                                          href={'https://oauth.net/2/grant-types/client-credentials/'}>OAuth 2.0 Client
                                          Credentials Grant</a>.
                                        </>}
                      />
                      <GrantTypeField checked={formik.values.refresh_token_grant}
                                      onChange={formik.handleChange}
                                      id={"refresh_token_grant"}
                                      label={"Refresh Token"} helpTitle={"Refresh Token Grant"}
                                      helpLong={
                                        <>
                                          The Refresh Token grant type is used by clients to exchange a refresh token
                                          for
                                          an access token when the access token has expired.
                                          This allows clients to continue to have a valid access token without further
                                          interaction with the user.
                                          <br/>
                                          For more information, see <a
                                          href={'https://oauth.net/2/grant-types/refresh-token/'}>OAuth 2.0 Refresh
                                          Token</a>.
                                        </>}
                      />
                      <GrantTypeField checked={formik.values.implicit_grant}
                                      onChange={formik.handleChange}
                                      id={"implicit_grant"}
                                      label={"Implicit (legacy)"}
                                      helpTitle={"Implicit Grant"}
                                      helpLong={
                                        <>
                                          The Implicit flow was a simplified OAuth flow previously recommended for
                                          native apps and JavaScript apps where
                                          the access token was returned immediately without an extra authorization code
                                          exchange step.
                                          <br/>
                                          For more information, see <a
                                          href={'https://oauth.net/2/grant-types/implicit/'}>OAuth 2.0 Implicit
                                          Grant</a>.
                                        </>}
                      />
                      <GrantTypeField checked={formik.values.password_grant}
                                      onChange={formik.handleChange}
                                      id={"password_grant"}
                                      label={"Password (legacy)"}
                                      helpTitle={"Password Grant"}
                                      helpLong={
                                        <>
                                          The Password grant type is a legacy way to exchange a user&apos;s credentials
                                          for an access token.
                                          Because the client application has to collect the user&apos;s password and
                                          send it to the authorization server,
                                          it is not recommended that this grant be used at all anymore.
                                          <br/>
                                          For more information, see <a
                                          href={'https://oauth.net/2/grant-types/password/'}>OAuth 2.0 Password
                                          Grant</a>.
                                        </>}
                      />
                    </FormGroup>
                  </div>
                </Stack>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
        <Stack
          alignItems="center"
          direction="row"
          justifyContent="flex-end"
          spacing={1}
        >
          <Button
            type="submit"
            variant="contained"
          >
            {saveLabelText}
          </Button>
        </Stack>
      </Stack>
    </form>
  );
};
