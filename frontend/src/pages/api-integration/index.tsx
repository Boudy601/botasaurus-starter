import { GetServerSideProps } from 'next/types'
import ApiIntegrationComponent from '../../components/ApiIntegrationComponent/ApiIntegrationComponent'
import { wrapAxiosErrors } from '../../components/AxiosErrorHoc'
import Description from '../../components/Description/Description'
import Tabs, { TabsId } from '../../components/PagesTabs/PagesTabs'
import Seo from '../../components/Seo'
import { Container, TabWrapper } from '../../components/Wrappers'
import AuthedDashboard from '../../components/AuthedDashboard'
import Api from '../../utils/api'
import { create_title } from '../../utils/common'

const Page = ({ ...props }: any) => {
  return (
    <>
      <Seo {...props} title={create_title(props, 'Api')} />
      <AuthedDashboard {...props}>
        <Container>
          <Description {...props} />
          <Tabs initialSelectedTab={TabsId.API_INTEGRATION} />
          <TabWrapper>
            <ApiIntegrationComponent {...props} />
          </TabWrapper>
        </Container>
      </AuthedDashboard>
    </>
  )
}

export const getServerSideProps: GetServerSideProps = wrapAxiosErrors(async ({}) => {
  const config = await Api.getApiConfig()
  return {
    props: config,
  }
})

export default Page
