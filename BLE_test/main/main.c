#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "esp_timer.h"
#include "nvs_flash.h"
#include "esp_bt.h"

#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/ble_hs_adv.h"
#include "host/ble_gap.h"
#include "host/util/util.h"

#define NODE_ID 'C'  // Vaihda A, B tai C

static const char *TAG = "BLE_RANGE";
static uint8_t own_addr_type;
static int64_t last_print[3];

static int gap_event(struct ble_gap_event *event, void *arg)
{
    if (event->type == BLE_GAP_EVENT_DISC) {

        struct ble_hs_adv_fields fields = {0};

        int rc = ble_hs_adv_parse_fields(
            &fields,
            event->disc.data,
            event->disc.length_data
        );

        if (rc != 0 || fields.name == NULL) {
            return 0;
        }

        if (fields.name_len != 6 ||
            memcmp(fields.name, "MESH_", 5) != 0) {
            return 0;
        }

        char peer = fields.name[5];

        if (peer < 'A' || peer > 'C' || peer == NODE_ID) {
            return 0;
        }

        int index = peer - 'A';
        int64_t now = esp_timer_get_time();

        if (now - last_print[index] >= 2000000LL) {
            last_print[index] = now;

            ESP_LOGI(TAG,
                     "NODE %c -> NODE %c | RSSI: %d dBm",
                     peer, NODE_ID, event->disc.rssi);
        }
    }

    return 0;
}

static void start_ble(void)
{
    struct ble_hs_adv_fields fields = {0};
    struct ble_gap_adv_params adv_params = {0};
    struct ble_gap_disc_params scan_params = {0};

    char name[] = "MESH_A";
    name[5] = NODE_ID;

    fields.flags = BLE_HS_ADV_F_DISC_GEN |
                   BLE_HS_ADV_F_BREDR_UNSUP;
    fields.name = (uint8_t *)name;
    fields.name_len = strlen(name);
    fields.name_is_complete = 1;

    int rc = ble_gap_adv_set_fields(&fields);
    if (rc != 0) {
        ESP_LOGE(TAG, "Adv fields error: %d", rc);
        return;
    }

    adv_params.conn_mode = BLE_GAP_CONN_MODE_NON;
    adv_params.disc_mode = BLE_GAP_DISC_MODE_GEN;
    adv_params.itvl_min = 160;
    adv_params.itvl_max = 160;

    rc = ble_gap_adv_start(
        own_addr_type,
        NULL,
        BLE_HS_FOREVER,
        &adv_params,
        gap_event,
        NULL
    );

    ESP_LOGI(TAG, "Advertising: %d", rc);

    scan_params.passive = 1;
    scan_params.filter_duplicates = 0;
    scan_params.itvl = 80;
    scan_params.window = 48;

    rc = ble_gap_disc(
        own_addr_type,
        BLE_HS_FOREVER,
        &scan_params,
        gap_event,
        NULL
    );

    ESP_LOGI(TAG, "Scanning: %d", rc);
}

static void on_sync(void)
{
    int rc = ble_hs_util_ensure_addr(0);
    if (rc != 0) {
        ESP_LOGE(TAG, "Address error: %d", rc);
        return;
    }

    rc = ble_hs_id_infer_auto(0, &own_addr_type);
    if (rc != 0) {
        ESP_LOGE(TAG, "Address type error: %d", rc);
        return;
    }

    // Aloitetaan normaalilla lähetysteholla.
    // Myöhemmin pienennetään tätä.
    esp_ble_tx_power_set(
        ESP_BLE_PWR_TYPE_ADV,
        ESP_PWR_LVL_N0
    );

    start_ble();
}

static void host_task(void *param)
{
    nimble_port_run();
    nimble_port_freertos_deinit();
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(nimble_port_init());

    ble_hs_cfg.sync_cb = on_sync;

    ESP_LOGI(TAG, "Starting NODE %c", NODE_ID);

    nimble_port_freertos_init(host_task);
}