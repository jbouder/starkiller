import httpx
import asyncio
import sys

async def verify_dashboards():
    url = "http://localhost:8000/api/v1/dashboards"
    
    print(f"🔍 Fetching dashboards from {url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            dashboards = response.json()
            
            print(f"✅ Successfully fetched {len(dashboards)} dashboards.")
            for d in dashboards:
                print(f" - [{d['id']}] {d['title']} ({len(d['data_sources'])} sources)")
                for ds in d['data_sources']:
                    print(f"   * {ds['name']} ({ds['source_type']})")
            
            if len(dashboards) > 0:
                # Test GET single dashboard
                d_id = dashboards[0]['id']
                print(f"\n🔍 Fetching single dashboard {d_id}...")
                response = await client.get(f"{url}/{d_id}")
                response.raise_for_status()
                print(f"✅ Successfully fetched dashboard: {response.json()['title']}")
                
                # Test PATCH dashboard
                print(f"\n🔍 Updating dashboard {d_id}...")
                response = await client.patch(f"{url}/{d_id}", json={"title": "Updated Title"})
                response.raise_for_status()
                print(f"✅ Successfully updated title to: {response.json()['title']}")
            
            return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(verify_dashboards())
    if not success:
        sys.exit(1)
